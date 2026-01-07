# 🧠 Volvox — AI-Powered Research Assistant

Volvox is an **AI-based research web application** designed to help researchers manage documents, interact with intelligent chatbots, and generate meaningful insights using **Retrieval-Augmented Generation (RAG)**.

It integrates modern LLM workflows, vector search, and scalable document management into a single platform.

---

## 🌐 Live Demo
🔗 **Volvox (Live):**  
https://volvox-alpha-frontend-suit.vercel.app

---

## 🚀 Features

### 🤖 RAG-Based Intelligent Chatbot
- Built using **LangChain** with **FAISS Vector Store**
- Context-aware conversations with persistent memory
- Chat sessions similar to ChatGPT
- View, continue, and delete specific chat sessions
- Maintains full conversation history per session
- Attach research documents to chatbot for grounded responses
- Powered by **Gemini 2.5 Flash**

---

### 📄 Research & Document Management
- Upload any type of research document
- Edit and delete uploaded documents
- Large file storage using **MongoDB GridFS**
- Attach documents to chatbot for RAG-based querying
- Search research documents by:
  - Name
  - Date
  - Time filters

---

### 📝 Research Summarization
- Summarize one or multiple research documents
- Designed for fast comprehension of large research material
- LLM-powered summarization pipelines

---

### ▶️ YouTube Video Summarization
- Provide a YouTube video URL
- Fetch transcripts using **YouTube Transcript API**
- Generate concise AI-based summaries
- Attach YouTube content to chatbot using RAG

---

### 🌐 Progressive Web App (PWA)
- Installable on mobile, laptop, and desktop
- Provides a near-native user experience

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- LangChain
- FAISS
- Uvicorn

### Frontend
- Next.js
- Progressive Web App (PWA)

### Database & Storage
- MongoDB
- GridFS (large file storage)

### AI / LLM
- Gemini 2.5 Flash
- Retrieval-Augmented Generation (RAG)

### Testing
- Postman

---

## 🧩 System Architecture

1. Users upload research documents
2. Documents are stored in MongoDB and indexed in FAISS
3. Queries are processed via a LangChain RAG pipeline
4. Relevant context is retrieved from vector store
5. Gemini 2.5 Flash generates grounded responses
6. Chat history is persisted per session

---

## 📦 Installation

### Backend Setup
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
npm install
npm run dev
```

### 📌 Use Cases

1. Academic researchers
2. Literature review automation
3. Thesis and paper analysis
4. Knowledge management systems
5. AI-powered research assistants
