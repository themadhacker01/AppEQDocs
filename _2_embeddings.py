import json, faiss
import numpy as np
import google.generativeai as genai

# Set the path to the JSON file containing the chunks
CHUNKS_FILE = 'appeq_chunks.json'

# Set the path to the FAISS index file
INDEX_FILE = 'faiss_chunks.index'

# Set up the API key for Google Generative AI
api_key = st.secrets['GEMINI_API_KEY']
genai.configure(api_key=api_key)

# -------------------
# Generate embeddings for the chunks using Google Generative AI
# -------------------
def generate_embeddings(chunks):    
    print('Generating embeddings for chunks...')

    embedded_chunks = []

    for chunk in chunks:
        response = genai.embed_content(
            model='models/embedding-001',
            content=chunk['text'],
            task_type='retrieval_document'
        )
        embedded_chunks.append({
            'chunk_id': chunk['chunk_id'],
            'title': chunk['title'],
            'url': chunk['url'],
            'text': chunk['text'],
            'embedding': response['embedding']
        })

    with open('embedded_chunks.json', 'w', encoding='utf-8') as f:
        json.dump(embedded_chunks, f, indent=2, ensure_ascii=False)

    print(f'✅ Embeddings created and stored for {len(embedded_chunks)} chunks.')
    return embedded_chunks

# -------------------
# Create a FAISS index from the embedded chunks
# -------------------
def create_faiss_index(embedded_chunks, index_file):
    print('Creating FAISS index to store embeddings...')

    embeddings = np.array([chunk['embedding'] for chunk in embedded_chunks]).astype('float32')

    metadata = [
        {key: chunk[key] for key in chunk if key != 'embedding'}
        for chunk in embedded_chunks
    ]

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, index_file)

    with open('appeq_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f'✅ FAISS index saved to {index_file}, metadata saved to appeq_metadata.json')

# -------------------
# Call the main function to execute the script
# -------------------
def main():
    print('Loading chunks from JSON file...')
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    embedded_chunks = generate_embeddings(chunks)
    create_faiss_index(embedded_chunks, INDEX_FILE)

# -------------------
# Executing the code using the main function
# -------------------
if __name__ == '__main__':
    main()
