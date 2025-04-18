import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Import the functions from 3_query.py
from _3_query import semantic_search, generate_summary, load_assets


# Set the paths for the FAISS index and metadata file
INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'appeq_metadata.json'
TOP_K = 5

# Load environment variables
load_dotenv()

# Set up the API key for Google Generative AI
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# -------------------
# Streamlit UI
# -------------------
def display_ui(index_file=INDEX_FILE, metadata_file=METADATA_FILE):
    st.header('AppEQ Support AI')

    st.sidebar.header('Have a question?')
    st.sidebar.subheader('Simply enter your query and we will answer it for you.')
    st.sidebar.write(
        '''
        This application allows you to respond to your query about the AppEQ features.
        It strictly adheres to material added in the help documentation and does not include any other information.
        '''
    )
    
    query = st.text_input('', placeholder='Type your question here...')

    if st.button('Search'):
        if query:
            index, metadata = load_assets(index_file, metadata_file)

            top_chunks = semantic_search(query, index, metadata, TOP_K)
            summary = generate_summary(query, top_chunks)

            st.subheader('Summary:')
            st.write(summary)

            st.subheader('Relevant Articles:')
            seen_articles = set()
            for chunk in top_chunks:
                if chunk["url"] not in seen_articles:
                    st.markdown(f'- [{chunk["title"]}]({chunk["url"]})')
                    seen_articles.add(chunk["url"])
        else:
            st.warning('Please enter a query to search.')

# -------------------
# Main execution
# -------------------
if __name__ == '__main__':
    display_ui()
