# 🤖 RAG Chatbot using Ollama + FAISS

A Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF documents and ask questions based on the document content.

The chatbot extracts text from PDFs, splits it into chunks, generates embeddings using HuggingFace models, stores embeddings in a FAISS vector database, retrieves relevant chunks, and generates contextual answers using a local LLM through Ollama.

---

# 🚀 Features

- 📄 Upload PDF documents
- 💬 Ask questions from uploaded PDFs
- 🧠 Semantic search using embeddings
- ⚡ FAISS vector database for fast retrieval
- 🤖 Local LLM support using Ollama
- 🔍 Source chunk visualization
- 📚 Context-aware answers using RAG pipeline
- 🖥️ Interactive Streamlit UI
- 🆓 Completely free and local setup

---

# 🛠️ Tech Stack

- Python
- Streamlit
- LangChain
- FAISS
- HuggingFace Embeddings
- Ollama
- pdfplumber

---

# 🧠 RAG Architecture

```text
PDF Document
     ↓
Text Extraction
     ↓
Text Chunking
     ↓
Embeddings Generation
     ↓
FAISS Vector Store
     ↓
Retriever
     ↓
Prompt + Context
     ↓
LLM (Gemma via Ollama)
     ↓
Final Response