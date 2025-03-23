import os
import uuid
import argparse
import pypdf
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
import tiktoken
from transformers import AutoTokenizer

# Carregar el tokenizer oficial de DeepSeek-R1
deepseek_tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1")


def extract_text_from_pdf(pdf_path):
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        return text
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return ""

def get_file_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def file_already_exists(collection, file_md5):
    """Check if a file with the given MD5 hash already exists in the collection."""
    results = collection.get(
        where={"file_md5": file_md5},  # Query by metadata
        include=["metadatas"]
    )
    return bool(results["metadatas"])  # If there's at least one match, return True

def tokenize_text_openai(text, model="gpt-3.5-turbo"):
    """Tokenizes text using OpenAI's encoding for better chunking."""
    encoder = tiktoken.encoding_for_model(model)
    tokens = encoder.encode(text)
    return tokens

def tokenize_text_deepseek(text):
    """Tokenitza text utilitzant el tokenizer de DeepSeek-R1."""
    tokens = deepseek_tokenizer.encode(text, add_special_tokens=False)
    return tokens

def split_text_into_chunks(text, chunk_size=200, chunk_overlap=50):
    """Splits text into chunks based on tokens, not characters."""
    tokens = tokenize_text_deepseek(text)
    chunks = []
    
    for i in range(0, len(tokens), chunk_size - chunk_overlap):
        chunk = tokens[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks

def process_file(file_path, collection_name, chroma_client):
    """Processa un fitxer, tokenitza el contingut amb DeepSeek-R1 i l'afegeix a ChromaDB."""
    file_id = str(uuid.uuid4())
    file_name = os.path.basename(file_path)
    file_md5 = get_file_md5(file_path)
    content = extract_text_from_pdf(file_path)

    print(f"Processing: {file_name} (MD5: {file_md5})")

    collection = chroma_client.get_or_create_collection(name=collection_name)

    if file_already_exists(collection, file_md5):
        print("File already exists in the collection. Skipping...")
        return

    # 🔹 Utilitzar DeepSeek-R1 per dividir el text en chunks
    chunks = split_text_into_chunks(content, chunk_size=200, chunk_overlap=50)
    
    for index, chunk in enumerate(chunks):
        chunk_id = f"{file_id}-{index}"
        chunk_text = deepseek_tokenizer.decode(chunk)  # Convertir tokens a text
        collection.add(
            documents=[chunk_text],  
            metadatas=[{
                "file_id": file_id,
                "chunk_id": chunk_id,
                "file_name": file_name,
                "file_md5": file_md5
            }],
            ids=[chunk_id]
        )

    print(f"Inserted {len(chunks)} DeepSeek-tokenized chunks into collection {collection_name}")

def process_input(input_path, collection_name, chroma_client):
    """Handles input, deciding if it's a file or directory."""
    if os.path.isfile(input_path):
        process_file(input_path, collection_name, chroma_client)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                process_file(file_path, collection_name, chroma_client)
    else:
        print("Invalid path provided.")

def run(database, collection, input):
    chroma_client = chromadb.PersistentClient(path=database)
    process_input(input, collection, chroma_client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files and directories for text chunking and store in ChromaDB.")
    parser.add_argument("-i", "--input", type=str, help="Path to a file or directory.")
    parser.add_argument("-c", "--collection", type=str, help="Collection name.", default="general")
    parser.add_argument("-db", "--database", type=str, help="Increase output verbosity.", default=".chroma_db")
    
    args = parser.parse_args()
    run(args.database, args.collection, args.input)
    