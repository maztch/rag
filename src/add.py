import os
import uuid
import argparse
import pypdf
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb


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

def process_file(file_path, collection_name, chroma_client):
    if not file_path.lower().endswith(".pdf"):
        print(f"Skipping non-PDF file: {file_path}")
        return

    """Processes a single file, splits content into chunks, and inserts into ChromaDB."""
    file_id = str(uuid.uuid4())
    file_name = os.path.basename(file_path)
    content = extract_text_from_pdf(file_path)
    file_md5 = get_file_md5(file_path)
    print(f"File Name: {file_name}")
    print(f"File MD5: {file_md5}")
    
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # check we don't have any file with the same md5
    query = collection.query(
        query_texts=[file_md5],
        n_results=1
    )
    if query["documents"]:
        print("File already exists in the collection.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100
    )
    chunks = text_splitter.split_text(content)
        
    for index, chunk in enumerate(chunks):
        chunk_id = f"{file_id}-{index}"
        collection.add(
            documents=[chunk],
            metadatas=[{"file_id": file_id, "chunk_id": chunk_id, "file_name": file_name, "file_md5": file_md5}],
            ids=[chunk_id]
        )
    print(f"Inserted {index} chunks into collection {collection_name}")

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
    