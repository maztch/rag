import argparse
import src.add as add
import src.status as status
import src.client as client
import src.reset as reset


def main():
    parser = argparse.ArgumentParser(description="Eina combinada.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Afegim el subparser per a cada comanda
    for cmd in ["add", "status", "client", "reset"]:
        subparser = subparsers.add_parser(cmd, help=f"run {cmd}")
        subparser.add_argument("-d", "--database", default=".chroma_db",  help="Path to the ChromaDB persist directory (default: 'chroma_db').")
        subparser.add_argument("-c", "--collection", default="general",  help="Collection name.")
        if cmd == "add":
            subparser.add_argument("-i", "--input", required=True, help="Fitxer o carpeta a afegir")
        

    args = parser.parse_args()

    # Executar la funció corresponent i passar-li la col·lecció
    if args.command == "add":
        add.run(args.database, args.collection, args.input)
    elif args.command == "status":
        status.run(args.database, args.collection)
    elif args.command == "client":
        client.run(args.database, args.collection)
    elif args.command == "reset":
        reset.run(args.database, args.collection)

if __name__ == "__main__":
    main()