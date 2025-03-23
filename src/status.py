import argparse
import chromadb
from chromadb.config import Settings

def run(database, collection):

    print(f"Loading ChromaDB from persist directory: {database}")

    client = chromadb.PersistentClient(path=database)

    collections = client.list_collections()

    if not collections:
        print("No collections found in the persisted ChromaDB instance.")
    else:
        print(f"Found {len(collections)} collection(s):\n")

        # Step 4: Iterate through each collection and summarize its contents
        for collection in collections:
            print(f"Collection Name: {collection}")

            # Get the collection object
            current_collection = client.get_collection(collection)

            # Count the number of items in the collection
            item_count = current_collection.count()
            print(f"  Number of Items: {item_count}")

            # Optionally, inspect metadata schema (if metadata exists)
            if item_count > 0:
                try:
                    # Fetch a sample item to inspect metadata structure
                    sample_item = current_collection.peek(limit=1)  # Peek at the first item
                    metadata_keys = sample_item.get("metadatas", [{}])[0].keys()
                    print(f"  Metadata Schema: {list(metadata_keys)}")
                except Exception as e:
                    print(f"  Error inspecting metadata: {e}")
            else:
                print("  Metadata Schema: No items in collection.")

            print("-" * 40)

def main():
    parser = argparse.ArgumentParser(description="Load ChromaDB from a persisted directory and list collections.")
    parser.add_argument(
        "--database", "-db",
        type=str,
        default=".chroma_db",  # Default directory
        help="Path to the ChromaDB persist directory (default: 'chroma_db')."
    )
    args = parser.parse_args()

    run(args.database)

if __name__ == "__main__":
    main()