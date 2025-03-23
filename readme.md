brew install miniconda
conda init zsh
conda create --name rag
conda activate rag
conda config --append channels conda-forge
conda install ollama langchain sentence-transformers chromadb pypdf pdfplumber tiktoken
 
