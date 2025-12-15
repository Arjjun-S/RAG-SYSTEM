# 📚 RAG Demo Application

A lightweight Retrieval-Augmented Generation (RAG) web application designed for **Render free tier deployment**. Perfect for portfolio demonstrations and technical interviews.

![RAG Architecture](https://img.shields.io/badge/Architecture-RAG-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Features

- **Document Upload**: Support for PDF and TXT files
- **Semantic Search**: FAISS-powered vector similarity search
- **Multi-Model Failover**: Automatic fallback across 3 free LLMs
- **Citations**: Answers include source references
- **Stateless Design**: Optimized for free tier deployment
- **Clean UI**: Simple, interview-ready interface

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React Frontend │────▶│  FastAPI Backend │────▶│  OpenRouter API │
│   (Vite)         │     │  (Python)        │     │  (Free LLMs)    │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                        ┌────────▼─────────┐
                        │   FAISS Index    │
                        │   (In-Memory)    │
                        └──────────────────┘
```

### RAG Flow

1. **Upload**: Document → Text Extraction → Chunking → Embedding → FAISS Index
2. **Query**: Question → Embedding → Semantic Search → Top-K Retrieval
3. **Generate**: Context + Question → LLM (with failover) → Answer + Citations

## 🧠 Models (Free Tier)

The application uses three OpenRouter models with automatic failover:

| Priority | Model | Context Limit | Timeout |
|----------|-------|---------------|---------|
| 1️⃣ Primary | Hermes 3 405B | 8,000 tokens | 8s |
| 2️⃣ Secondary | Mistral 7B | 4,000 tokens | 8s |
| 3️⃣ Fallback | Llama 3.3 70B | 3,000 tokens | 8s |

### Failover Strategy

```
Request → Model 1 (Hermes)
              │
              ▼ Timeout/Error?
          Model 2 (Mistral)
              │
              ▼ Timeout/Error?
          Model 3 (Llama)
              │
              ▼ All failed?
          Return error
```

## ⚡ Free Tier Optimizations

| Optimization | Implementation |
|-------------|----------------|
| No persistent storage | FAISS recreated on startup |
| Lightweight embeddings | all-MiniLM-L6-v2 (22M params) |
| Limited context | Max 3 chunks per query |
| Aggressive timeouts | 8 seconds per model |
| Small chunk size | 500-700 tokens |
| In-memory only | No database required |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenRouter API key ([Get free key](https://openrouter.ai/))

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENROUTER_API_KEY="your-api-key-here"

# Run server
uvicorn main:app --host 0.0.0.0 --port 10000 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Open http://localhost:3000 in your browser.

## 📁 Project Structure

```
rag-app/
│
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration & models
│   ├── llm_router.py        # Multi-model failover
│   ├── ingest.py            # Document ingestion
│   ├── retriever.py         # FAISS vector store
│   ├── qa.py                # RAG pipeline
│   ├── utils/
│   │   ├── loaders.py       # PDF/TXT extraction
│   │   └── chunker.py       # Text chunking
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Upload.jsx   # File upload
│   │   │   ├── Chat.jsx     # Q&A interface
│   │   │   └── Sources.jsx  # Citations display
│   │   ├── App.jsx          # Main component
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Styles
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/upload` | Upload document |
| POST | `/ask` | Ask question |
| GET | `/stats` | System statistics |
| POST | `/clear` | Clear all documents |

### Example Requests

**Upload Document:**
```bash
curl -X POST http://localhost:10000/upload \
  -F "file=@document.pdf"
```

**Ask Question:**
```bash
curl -X POST http://localhost:10000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "top_k": 3}'
```

## 🌐 Deployment (Render)

### Backend Deployment

1. Create a new **Web Service** on Render
2. Connect your GitHub repository
3. Configure:
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Add environment variable:
   - `OPENROUTER_API_KEY`: Your API key

### Frontend Deployment

1. Create a new **Static Site** on Render
2. Connect your GitHub repository
3. Configure:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add environment variable:
   - `VITE_API_URL`: Your backend URL (e.g., `https://your-backend.onrender.com`)

## 💡 Example Questions

After uploading a document, try these questions:

- "What is the main topic of this document?"
- "Summarize the key points."
- "What are the conclusions mentioned?"
- "Who are the main people or organizations discussed?"
- "What dates or timeframes are mentioned?"

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Yes |
| `SITE_URL` | Your site URL (for OpenRouter) | No |
| `SITE_NAME` | Your site name (for OpenRouter) | No |
| `VITE_API_URL` | Backend API URL (frontend) | Production only |

### Customization

Edit `backend/config.py` to adjust:
- Chunk size and overlap
- Number of retrieved chunks
- Model priorities and timeouts
- Prompt template

## ⚠️ Limitations

This is a **demonstration project** with intentional limitations:

- **No persistence**: Data is lost on restart
- **Memory constraints**: Limited by free tier RAM
- **Rate limits**: Subject to OpenRouter free tier limits
- **No authentication**: Open access by design
- **Single user**: Not designed for concurrent heavy usage

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.10+ |
| Vector Store | FAISS (in-memory) |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| LLM API | OpenRouter (free tier) |
| Frontend | React 18, Vite |
| Styling | Plain CSS |
| Deployment | Render (free tier) |

## 📄 License

MIT License - Feel free to use for your portfolio!

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai/) for free LLM access
- [Sentence Transformers](https://sbert.net/) for embeddings
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Vite](https://vitejs.dev/) for frontend tooling

---

**Built for learning and demonstration purposes.** Perfect for showing RAG fundamentals in interviews! 🎯