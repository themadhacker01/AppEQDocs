import json, os, faiss
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai


# Set the path to the JSON file containing the chunks
CHUNKS_FILE = 'chunks.json'

# Set the path to the FAISS index file
INDEX_FILE = 'faiss_chunks.index'

# Load environment variables from .env
load_dotenv()

# Set up the API key for Google Generative AI
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)


# -------------------
# Generate embeddings for the chunks using Google Generative AI
# -------------------
def generate_embeddings(chunks):    
    print('Generating embeddings for chunks...')

    # Initialize an empty list to store the embedded chunks
    embedded_chunks = []

    # Loop through each chunk and generate its embedding
    for chunk in chunks:
        # Generate the embedding for the chunk using the Google GenAI API
        response = genai.embed_content(
            model='models/embedding-001',
            content=chunk['text'],
            task_type='retrieval_document'
        )
        # Append the chunk with its embedding to the list
        embedded_chunks.append({
            'chunk_id': chunk['chunk_id'],
            'article_id': chunk['article_id'],
            'title': chunk['title'],
            'url': chunk['url'],
            'text': chunk['text'],
            'embedding': response['embedding']
        })
    
    # Save the embedded chunks to a JSON file for debugging
    with open('embedded_chunks.json', 'w', encoding='utf-8') as f:
        json.dump(embedded_chunks, f, indent=2, ensure_ascii=False)

    # Return the list of embedded chunks
    print(f'✅ Embeddings created and stored for {len(embedded_chunks)} chunks.')
    return embedded_chunks


# -------------------
# Create a FAISS index from the embedded chunks
# -------------------
def create_faiss_index(embedded_chunks, index_file):
    print('Creating FAISS index to store embeddings...')

    # Extract the embeddings and convert them to a NumPy array
    # Convert them to float32 as required by FAISS
    embeddings = np.array([chunk['embedding'] for chunk in embedded_chunks]).astype('float32')

    # Removes the 'embedding' key from embedded_chunks to create metadata
    metadata = [
        {key: chunk[key] for key in chunk if key != "embedding"}
        for chunk in embedded_chunks
    ]

    # Create a FAISS index and add the embeddings to it
    dim = embeddings.shape[1]
    # Use L2 distance for nearest neighbor search
    index = faiss.IndexFlatL2(dim)
    # Add the embeddings to the index
    index.add(embeddings)

    # Save the index to a file
    faiss.write_index(index, index_file)

    # Save the chunk metadata - chunk ID, article ID, title, URL, text
    with open('metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f'✅ FAISS index saved to {index_file}, metadata saved to metadata.json')


# -------------------
# Call the main function to execute the script
# -------------------
def main():
    # Load the chunks from the JSON file
    print('Loading chunks from JSON file...')
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Generate embeddings for the chunks
    embedded_chunks = generate_embeddings(chunks)
    
    # Create a FAISS index from the embedded chunks
    create_faiss_index(embedded_chunks, INDEX_FILE)


# -------------------
# Executing the code using the main function
# -------------------
if __name__ == '__main__':
    main()