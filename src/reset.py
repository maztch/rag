# reset_database.py
import argparse
import chromadb
import sys

def confirm_action(prompt="Are you sure? (y/n): "):
    """Asks the user for confirmation before proceeding."""
    while True:
        choice = input(prompt).lower()
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            print("Operation canceled.")
            sys.exit(0)
        else:
            print("Please enter 'y' or 'n'.")

def reset_database(persist_directory="chroma_db", collection_name=None):
    """
    Resets the ChromaDB database by deleting a specific collection or all collections.
    
    Args:
        collection_name (str, optional): Name of the collection to delete. If None, deletes all collections.
    """
    client = chromadb.PersistentClient(path=persist_directory)
    
    if collection_name:
        if not confirm_action(f"Are you sure you want to delete the collection '{collection_name}'? (y/n): "):
            return
        try:
            client.delete_collection(name=collection_name)
            print(f"Collection '{collection_name}' has been deleted.")
        except ValueError:
            print(f"Collection '{collection_name}' does not exist.")
    else:
        if not confirm_action("Are you sure you want to delete ALL collections? (y/n): "):
            return
        collections = client.list_collections()
        for collection in collections:
            client.delete_collection(name=collection)
        print("All collections have been deleted.")

def run(database, collection_name):
    """Main function to handle command-line arguments."""
    
    # Reset the database
    reset_database(database, collection_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset ChromaDB Database")
    parser.add_argument("-c", "--collection", type=str, help="Name of the collection to delete. If not provided, all collections will be deleted.")
    parser.add_argument("-db", "--database", type=str, default=".chroma_db", help="Directory to persist ChromaDB data (optional, defaults to 'chroma_db').")
    
    args = parser.parse_args()

    run(args.database, args.collection)