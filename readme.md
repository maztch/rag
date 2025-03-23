RAG
===

This is a basic rag for home usage. I have tested it with my ollama with deepseek-r1


# Install

brew install miniconda
conda init zsh
conda create --name rag
conda activate rag
conda config --append channels conda-forge
conda install ollama langchain sentence-transformers chromadb pypdf pdfplumber tiktoken

# Usage

Actually there are 3 branches, basic, deepseek and gpt (openai).

You can swiths to the desired one and run rag

```bash
python rag.py add -i {input file}
```

Check th db status

```bash
python rag.py status
```

Run the chat client that will use the files as a context

```bash
python rag.py client
```

Reset the database if you want to reestart

```bash
python rag.py reset
```


## Other

Just for the samples using tokens, you may need to download the model.

    pip install -U "huggingface_hub[cli]"

    huggingface-cli download deepseek-ai/deepseek-llm-7b