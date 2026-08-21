# 🤖 YouTube Transcript RAG Assistant

A Retrieval-Augmented Generation (RAG) pipeline built with Python and LangChain that automatically fetches YouTube video transcripts, indexes them into a vector database (ChromaDB), and answers user questions strictly based on the video context using Hugging Face's inference API.

---

## 📌 Features

- 📹 **Automated Transcript Extraction**: Fetches transcripts directly from YouTube videos via `youtube-transcript-api`.
- ✂️ **Smart Text Chunking**: Splits video transcripts into manageable context chunks using `RecursiveCharacterTextSplitter`.
- 🔍 **Vector Search & Persistence**: Generates semantic embeddings with `sentence-transformers/all-MiniLM-L6-v2` and stores them in a local `ChromaDB` vector store.
- 🎯 **Strict Context-Grounded QA**: Uses custom prompt templates ensuring responses are strictly grounded in the video transcript (minimizing hallucinations).
- ⚡ **Hugging Face LLM Integration**: Powered by open-source LLMs hosted via Hugging Face Serverless Inference.

---

## 🏗️ Architecture & Workflow

```text
[ YouTube Video ID ]
         │
         ▼
[ YouTube Transcript API ] ──▶ Raw Transcript Text
         │
         ▼
[ RecursiveCharacterTextSplitter ] ──▶ Text Chunks
         │
         ▼
[ HuggingFace Embeddings ] ──▶ Vector Embeddings
         │
         ▼
[ ChromaDB Vector Store ] (Saved locally in ./chroma_db)
         │
         ▼
[ User Query ] ──▶ [ Similarity Search Retriever ] ──▶ Context Chunks
                                                               │
                                                               ▼
[ HuggingFace Inference Endpoint ] ◄── [ RAG Prompt Template ]
         │
         ▼
  [ Final Answer ]
