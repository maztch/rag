import chromadb
import argparse
import ollama

OLLAMA_MODEL = "deepseek-r1"  # You can use another model like "llama2", "gemma", etc.

def query_chroma(query, collection):
    results = collection.query(
        query_texts=[query],
        n_results=3  # Get the top 3 most relevant chunks
    )
    return results["documents"][0] if results["documents"] else []

def generate_response(user_input, collection):
    # Retrieve relevant chunks from ChromaDB
    relevant_chunks = query_chroma(user_input, collection)
    context = "\n".join(relevant_chunks) if relevant_chunks else "No relevant documents found."

    # Generate a response using Ollama
    prompt = f"Context:\n{context}\n\nUser Question: {user_input}\n\nAnswer:"
    response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
    
    return response['message']['content']

def run(database, collection_name):
    client = chromadb.PersistentClient(path=database)
    collection = client.get_or_create_collection(name=collection_name)

    while True:
        user_input = input("\nAsk a question (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break

        response = generate_response(user_input, collection)
        print("\nOllama's Response:\n", response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files and directories for text chunking and store in ChromaDB.")
    parser.add_argument("-c", "--collection", type=str, help="Collection name.", default="general")
    parser.add_argument("-db", "--database", type=str, help="Path to the ChromaDB persist directory (default: 'chroma_db').", default=".chroma_db")
    
    args = parser.parse_args()

    run(args.database, args.collection)
