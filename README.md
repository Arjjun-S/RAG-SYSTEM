<img width="640" height="108" alt="Screenshot 2025-12-17 at 11 33 14 AM" src="https://github.com/user-attachments/assets/4b15ed20-0fa1-493b-b570-8ae878922f5d" />

A lightweight Retrieval-Augmented Generation (RAG) web application designed for free-tier deployment. Upload documents, ask questions, and get accurate answers with source citations.

**Live Demo:** [https://rag-frontend-mldy.onrender.com/](https://rag-frontend-mldy.onrender.com/)

---

## Screenshots

### Home View
<img width="1280" height="800" alt="Screenshot 2025-12-17 at 11 09 49 AM" src="https://github.com/user-attachments/assets/2b821cf1-5a9e-4cae-86a0-edd4aaa735eb" />
*The main interface with upload section and chat*

### Document Upload
<img width="1280" height="800" alt="Screenshot 2025-12-17 at 11 10 11 AM" src="https://github.com/user-attachments/assets/31dda62f-99b9-4e91-8f7d-98d332b22ebb" />
*Uploading a document to the knowledge base*

### Asking Questions
<img width="1280" height="800" alt="Screenshot 2025-12-17 at 11 11 24 AM" src="https://github.com/user-attachments/assets/af20f162-172b-4c90-b0fb-edf747b31d58" />
*Submitting a question about the uploaded documents*

### Answer with Citations
<img width="622" height="776" alt="Screenshot 2025-12-17 at 11 12 25 AM" src="https://github.com/user-attachments/assets/ea0d4cc7-bc8c-47bc-93ff-271eda18e84a" />

*Response with source citations from the uploaded documents*

---

## What is RAG?

Retrieval-Augmented Generation (RAG) is an AI technique that combines information retrieval with text generation. Instead of relying solely on a language model's training data, RAG:

1. **Retrieves** relevant information from your uploaded documents
2. **Augments** the prompt with this retrieved context
3. **Generates** an answer grounded in your actual data

This significantly reduces hallucination and provides accurate, source-backed responses.

---

## System Architecture

```
                                    RAG Mini Architecture
                                    
    +------------------+          +----------------------+          +-------------------+
    |                  |          |                      |          |                   |
    |  React Frontend  |  <---->  |   FastAPI Backend    |  <---->  |  OpenRouter API   |
    |     (Vite)       |   HTTP   |      (Python)        |   HTTPS  |   (Free LLMs)     |
    |                  |          |                      |          |                   |
    +------------------+          +----------+-----------+          +-------------------+
                                             |
                                             |
                                  +----------v-----------+
                                  |                      |
                                  |  TF-IDF Vectorizer   |
                                  |    (In-Memory)       |
                                  |                      |
                                  +----------------------+
```

### Data Flow

```
DOCUMENT INGESTION:
                                                                        
  PDF/TXT File --> Text Extraction --> Text Chunking --> TF-IDF Vectorization --> In-Memory Store
                                            |
                                            v
                                   (600 chars per chunk)


QUESTION ANSWERING:

  User Question --> TF-IDF Query --> Retrieve Top 3 Chunks --> Build Context
                                                                     |
                                                                     v
                                                          Prompt + Context --> LLM
                                                                                 |
                                                                                 v
                                                                    Answer + Citations --> User
```

---

## How It Works

### 1. Document Upload

When you upload a document (PDF or TXT):

- **Text Extraction**: The system extracts raw text from the file using `pypdf` for PDFs
- **Chunking**: Text is split into overlapping chunks of ~600 characters with 100 character overlap
- **Vectorization**: Each chunk is converted to a TF-IDF vector for similarity matching
- **Storage**: Vectors and text are stored in memory (no database required)

### 2. Question Processing

When you ask a question:

- **Query Vectorization**: Your question is converted to a TF-IDF vector
- **Similarity Search**: The system finds the 3 most relevant chunks using cosine similarity
- **Context Building**: Retrieved chunks are combined into a context block

### 3. Answer Generation

The context and question are sent to an LLM:

- **Prompt Engineering**: A carefully designed prompt instructs the model to answer based only on the provided context
- **Multi-Model Failover**: If one model times out, the system automatically tries the next
- **Citation Extraction**: The answer includes references to source documents

---

## Models and Failover Strategy

RAG Mini uses three OpenRouter models with automatic failover:

| Priority | Model | Description |
|----------|-------|-------------|
| Primary | NousResearch Hermes 3 405B | Large, high-quality responses |
| Secondary | Mistral 7B Instruct | Fast, reliable fallback |
| Tertiary | Meta Llama 3.3 70B | Final fallback option |

### Failover Logic

```
Request --> Hermes 3 405B (8s timeout)
                |
                +--> Success? Return response
                |
                +--> Timeout/Error? --> Mistral 7B (8s timeout)
                                            |
                                            +--> Success? Return response
                                            |
                                            +--> Timeout/Error? --> Llama 3.3 70B (8s timeout)
                                                                        |
                                                                        +--> Success? Return response
                                                                        |
                                                                        +--> All failed? Return error
```

Each model has an 8-second timeout. This ensures reasonable response times even when free-tier models experience high load.

---

## Accuracy Considerations

### What Makes RAG Mini Accurate

1. **Grounded Responses**: Answers are based on your uploaded documents, not general training data
2. **Source Citations**: Every answer shows which document chunks were used
3. **Focused Context**: Only the top 3 most relevant chunks are used, reducing noise
4. **Instruction Tuning**: The prompt explicitly tells the model to say "I don't know" if the answer isn't in the context

### Limitations Affecting Accuracy

1. **TF-IDF vs Semantic Search**: TF-IDF matches keywords, not meaning. Synonyms or paraphrased content may not be retrieved
2. **Chunk Boundaries**: Important information split across chunks may lose context
3. **Free Model Variability**: Free-tier models may have inconsistent quality
4. **No Persistence**: All data is lost when the server restarts

### Accuracy Tips

- Upload focused, relevant documents
- Ask specific questions with keywords that appear in your documents
- Keep documents under 50 pages for best results
- If an answer seems wrong, rephrase your question

---

## Technical Specifications

| Component | Implementation |
|-----------|----------------|
| Backend Framework | FastAPI (Python) |
| Frontend Framework | React 18 + Vite |
| Vector Search | TF-IDF with scikit-learn |
| PDF Processing | pypdf |
| LLM Provider | OpenRouter (free tier) |
| Deployment | Render (free tier) |

### Configuration Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Chunk Size | 600 characters | Balance between context and precision |
| Chunk Overlap | 100 characters | Preserve context across boundaries |
| Top-K Retrieval | 3 chunks | Limit context size for free models |
| Model Timeout | 8 seconds | Ensure responsive failover |
| Max Features | 5000 | TF-IDF vocabulary limit |

---

## Project Structure

```
RAG-SYSTEM/
|
+-- backend/
|   +-- main.py              # FastAPI application and endpoints
|   +-- config.py            # Configuration and model settings
|   +-- llm_router.py        # Multi-model failover logic
|   +-- ingest.py            # Document ingestion pipeline
|   +-- retriever.py         # TF-IDF vector search
|   +-- qa.py                # Question-answering pipeline
|   +-- utils/
|   |   +-- loaders.py       # PDF and TXT file loaders
|   |   +-- chunker.py       # Text chunking logic
|   +-- requirements.txt     # Python dependencies
|
+-- frontend/
|   +-- src/
|   |   +-- components/
|   |   |   +-- Upload.jsx   # File upload component
|   |   |   +-- Chat.jsx     # Chat interface
|   |   |   +-- Sources.jsx  # Citations display
|   |   +-- App.jsx          # Main application
|   |   +-- main.jsx         # Entry point
|   |   +-- index.css        # Styles
|   +-- public/              # Static assets
|   +-- package.json         # Node dependencies
|   +-- vite.config.js       # Vite configuration
|
+-- render.yaml              # Render deployment config
+-- runtime.txt              # Python version specification
+-- README.md
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/upload` | Upload a document (PDF/TXT) |
| POST | `/ask` | Ask a question |
| GET | `/stats` | Get system statistics |
| POST | `/clear` | Clear all documents |

### Upload Document

```bash
curl -X POST https://your-backend.onrender.com/upload \
  -F "file=@document.pdf"
```

### Ask Question

```bash
curl -X POST https://your-backend.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "top_k": 3}'
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenRouter API key (free at [openrouter.ai](https://openrouter.ai/))

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENROUTER_API_KEY="your-api-key"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## Deployment on Render

### Backend (Web Service)

1. Create a Web Service on Render
2. Connect your GitHub repository
3. Set Root Directory: `backend`
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable: `OPENROUTER_API_KEY`

### Frontend (Static Site)

1. Create a Static Site on Render
2. Connect your GitHub repository
3. Set Root Directory: `frontend`
4. Set Build Command: `npm install && npm run build`
5. Set Publish Directory: `dist`
6. Add Environment Variable: `VITE_API_URL` (your backend URL)

---

## Important Usage Guidelines

This application runs on free-tier infrastructure. Please be considerate:

### Do

- Upload small to medium documents (under 50 pages)
- Ask focused, specific questions
- Wait for responses before sending new requests
- Clear documents when you're done testing

### Do Not

- Upload large files or many documents at once
- Send rapid-fire requests
- Use this for production workloads
- Rely on data persistence (everything resets on restart)

### Why These Guidelines Matter

- **Free Tier Limits**: OpenRouter free models have rate limits
- **Shared Resources**: The Render free tier has limited memory and CPU
- **No Queue System**: Concurrent requests may cause failures
- **Stateless Design**: Memory is limited; too many documents will cause crashes

---

## Limitations

| Limitation | Reason |
|------------|--------|
| No data persistence | Free tier has no disk storage |
| Memory constraints | Limited to ~512MB on free tier |
| Cold starts | Server sleeps after inactivity |
| Rate limits | OpenRouter free tier restrictions |
| No authentication | Designed for demos only |
| Single region | Higher latency for distant users |

---

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [React](https://react.dev/) - Frontend library
- [Vite](https://vitejs.dev/) - Frontend build tool
- [scikit-learn](https://scikit-learn.org/) - TF-IDF vectorization
- [pypdf](https://pypdf.readthedocs.io/) - PDF text extraction
- [OpenRouter](https://openrouter.ai/) - LLM API access
- [Render](https://render.com/) - Deployment platform

---

## License

MIT License - Free to use and modify.

---

**Note**: This is a demonstration project designed for learning and portfolio purposes. For production use cases, consider using persistent vector databases, semantic embeddings, and paid LLM tiers.
