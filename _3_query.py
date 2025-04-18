import json
import faiss
import numpy as np
import google.generativeai as genai

INDEX_FILE = 'faiss_chunks.index'
METADATA_FILE = 'appeq_metadata.json'
TOP_K = 3
MODEL_NAME = 'models/gemini-1.5-pro-002'

# Set up the API key for Google Generative AI
api_key = st.secrets['GEMINI_API_KEY']
genai.configure(api_key=api_key)

# -------------------
# Loads the FAISS index and metadata from the specified paths
# -------------------
def load_assets(index_path, metadata_path):
    print('Loading assets...')
    
    index = faiss.read_index(index_path)

    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    return index, metadata

# -------------------
# Embed the user query and run semantic search on FAISS
# -------------------
def semantic_search(query, index, metadata, k):
    print('Performing semantic search...')

    response = genai.embed_content(
        model='models/embedding-001',
        content=query,
        task_type='retrieval_query'
    )
    query_embedding = np.array(response['embedding']).astype('float32').reshape(1, -1)

    distances, indices = index.search(query_embedding, k)
    results = [metadata[i] for i in indices[0]]

    return results


# -------------------
# Generate a summary from the top results using Gemini
# -------------------
def generate_summary(query, chunks):
    print('Generating summary...')

    context = '\n\n'.join([chunk['text'] for chunk in chunks])

    model = genai.GenerativeModel(model_name=MODEL_NAME)

    init_prompt = (
        '''
        Use the context that is relevant to the query.
        Provide some additional informatin in the response, if needed.
        Be concise when you respond.
        Do not change the terminology or keywords used in the document.
        The response must be coherent and easy to read.
        If you do not know the answer, say "I don't know".
        If the answer is not in the context, say "The answer is not in the context".
        Do not make up answers or provide information that is not in the context.
        Do not include any disclaimers or unnecessary information.
        '''
        f'\n\Query:\n{query}'
        f'\n\nContext:\n{context}'
    )
    init_response = model.generate_content(init_prompt)
    print('Summary generated.')

    return init_response.text

# -------------------
# Main function to test the flow
# -------------------
def main(index_path=INDEX_FILE, metadata_path=METADATA_FILE, top_k=TOP_K):
    relevant_articles = []
    
    index, metadata = load_assets(index_path, metadata_path)

    query = input('Enter your search query: ')

    top_chunks = semantic_search(query, index, metadata, top_k)

    summary = generate_summary(query, top_chunks)

    print('\n🔎 Summary:')
    print(summary)

    print('\n📄 Relevant Articles:')
    for chunk in top_chunks:
        print(f'- {chunk["title"]}: {chunk["url"]}')


# -------------------
# Executing the code using the main function
# -------------------
if __name__ == '__main__':
    main()