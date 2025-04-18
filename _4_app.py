import streamlit as st
import json
import google.generativeai as genai

# Custom functions
from _1_scraper import main as scrape_articles, chunk_articles
from _2_embeddings import generate_embeddings, create_faiss_index
from _3_query import semantic_search, generate_summary, load_assets

# Paths
INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'appeq_metadata.json'
CHUNKS_FILE = 'article_chunks.json'
ARTICLES_FILE = 'appeq_articles.json'
EMBEDDED_FILE = 'embedded_chunks.json'
TOP_K = 5

# Set up the API key for Google Generative AI
api_key = st.secrets['GEMINI_API_KEY']
genai.configure(api_key=api_key)

# Session state for control
if 'refreshing' not in st.session_state:
    st.session_state.refreshing = False
if 'searching' not in st.session_state:
    st.session_state.searching = False

# UI
st.header('AppEQ Support AI')
st.sidebar.header('Have a question?')
st.sidebar.subheader('Simply enter your query and we will answer it for you.')
st.sidebar.write(
    '''
    This application allows you to respond to your query about the AppEQ features.
    It strictly adheres to material added in the help documentation and does not include any other information.
    '''
)
with st.sidebar:
    refresh = st.button('Refresh', disabled=st.session_state.searching)

query = st.text_input('', placeholder='Type your question here...', disabled=st.session_state.refreshing)

if refresh:
    st.session_state.refreshing = True
    with st.spinner('Refreshing data, please wait...'):
        scrape_articles()  # creates appeq_articles.json

        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        chunk_articles(articles)  # creates article_chunks.json

        with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        embedded = generate_embeddings(chunks)  # creates embedded_appeq_chunks.json
        create_faiss_index(embedded, INDEX_FILE)  # creates faiss index and metadata
    st.success('✅ Data refreshed successfully')
    st.session_state.refreshing = False

if st.button('Search', disabled=st.session_state.refreshing):
    if query:
        st.session_state.searching = True
        with st.spinner('Searching...'):
            index, metadata = load_assets(INDEX_FILE, METADATA_FILE)
            top_chunks = semantic_search(query, index, metadata, TOP_K)
            summary = generate_summary(query, top_chunks)

        st.subheader('Summary:')
        st.write(summary)

        st.subheader('Relevant Articles:')
        seen_articles = set()
        for chunk in top_chunks:
            if chunk['url'] not in seen_articles:
                st.markdown(f'- [{chunk["title"]}]({chunk["url"]})')
                seen_articles.add(chunk['url'])
        st.session_state.searching = False
    else:
        st.warning('Please enter a query to search.')