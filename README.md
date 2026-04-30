# RAGSense — Agentic AI Document Assistant

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://python.langchain.com/langgraph/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-Mistral_3.5-76b900.svg)](https://build.nvidia.com/)
[![FAISS](https://img.shields.io/badge/FAISS-VectorDB-blueviolet.svg)](https://github.com/facebookresearch/faiss)

## Overview

**RAGSense** is an intelligent Retrieval-Augmented Generation system powered by agentic AI. It combines adaptive query routing, document retrieval, and LLM capabilities to provide accurate, context-aware answers.

The system classifies each query and routes it to the best pipeline — indexed documents, general knowledge, or real-time web search — using LangGraph for workflow orchestration and NVIDIA NIM as the LLM backend.

---

## Key Features

### Intelligent Query Routing
- **Adaptive Classification** — automatically routes queries to the most appropriate pipeline
- **Three Query Types:**
  - **Index** — answerable from uploaded documents
  - **General** — answerable with common knowledge
  - **Search** — requires real-time web search

### Advanced RAG Pipeline
- **Document Processing** — chunking and embedding via NVIDIA NV-EmbedQA
- **Vector Search** — FAISS-based similarity retrieval with dynamic retriever
- **Relevance Grading** — automatic evaluation of retrieved documents
- **Query Rewriting** — optimises queries for better retrieval on retry

### Agentic Architecture
- **ReAct Framework** — Reasoning + Acting pattern for multi-step tool use
- **Dynamic Retrieval** — new uploads are immediately searchable (no restart needed)
- **Tool Integration** — retriever tools and Tavily web search

### Auth & Session Management
- **Built-in Auth** — JWT-based login/signup (no external auth service needed)
- **MongoDB Backend** — persistent chat history and session tracking
- **API Token Flow** — `/api/init` → `/api/create_user` → `/api/login`

### User Interface
- **Streamlit Web App** — dark-themed chat interface with document upload sidebar
- **Loading States** — spinners for queries, uploads, login, and backend connection
- **File Support** — PDF and TXT uploads

---

## Architecture

![App Architecture](./App_Architecture.png)


### Graph Nodes

| Node | Purpose |
|------|---------|
| `query_analysis` | Classifies query → `index`, `general`, or `search` |
| `retriever` | Retrieves documents from FAISS via ReAct agent |
| `grade` | Evaluates relevance of retrieved documents |
| `rewrite` | Rewrites query for better retrieval on retry |
| `generate` | Generates final answer from context |
| `web_search` | Real-time web search via Tavily |
| `general_llm` | General knowledge answers (no retrieval needed) |

---

## Project Structure

```
Adaptive-Rag-main/
├── app/                              # FastAPI backend
│   ├── main.py                       # Application entry point
│   ├── api/
│   │   ├── auth.py                   # Auth routes (init, create_user, login)
│   │   └── routes.py                 # RAG routes (query, upload)
│   ├── config/
│   │   ├── settings.py               # YAML config loader
│   │   └── prompts.yaml              # LLM prompt templates
│   ├── core/
│   │   └── config.py                 # Environment settings
│   ├── db/
│   │   └── mongo_client.py           # MongoDB (Motor) client
│   ├── llms/
│   │   └── openai.py                 # NVIDIA NIM / Mistral-3.5-128B via OpenAI-compat API
│   ├── memory/
│   │   ├── chat_history_mongo.py     # MongoDB-backed chat history
│   │   └── chathistory_in_memory.py  # In-memory fallback
│   ├── models/
│   │   ├── state.py                  # LangGraph state schema
│   │   ├── query_request.py          # Query request model
│   │   ├── grade.py                  # Relevance grade model
│   │   ├── route_identifier.py       # Route classification model
│   │   └── verification_result.py    # Answer verification model
│   ├── rag/
│   │   ├── graph_builder.py          # LangGraph workflow construction
│   │   ├── retriever_setup.py        # FAISS + NVIDIA embeddings + DynamicRetriever
│   │   ├── document_upload.py        # PDF/TXT processing pipeline
│   │   └── reAct_agent.py            # ReAct agent with string prompt template
│   └── tools/
│       ├── common_tools.py           # Description enhancement via LLM
│       └── graph_tools.py            # Routing and grading decision tools
│
├── streamlit_app/                    # Streamlit frontend
│   ├── home.py                       # Login / Signup page (tabbed)
│   ├── pages/
│   │   └── chat.py                   # Chat interface + document upload
│   ├── utils/
│   │   └── api_client.py             # Backend API client (single BASE_URL)
│   └── .streamlit/
│       └── config.toml               # Dark theme configuration
│
├── .env                              # Environment variables (not committed)
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## API Endpoints

### Auth Endpoints (prefix: `/api`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/init` | Generate an API token for the session |
| `POST` | `/api/create_user` | Register a new user (requires `X-API-TOKEN` header) |
| `POST` | `/api/login` | Authenticate and receive a JWT (requires `X-API-TOKEN` header) |

### RAG Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/rag/query` | Process a RAG query |
| `POST` | `/rag/documents/upload` | Upload a PDF/TXT document for indexing |

### Example Requests

**Initialize session:**
```bash
curl -X POST http://localhost:8000/api/init
# → {"api_token": "abc123..."}
```

**Create user:**
```bash
curl -X POST http://localhost:8000/api/create_user \
  -H "X-API-TOKEN: abc123..." \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/login \
  -H "X-API-TOKEN: abc123..." \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'
# → {"jwt": "eyJhbG..."}
```

**Upload a document:**
```bash
curl -X POST http://localhost:8000/rag/documents/upload \
  -H "X-Description: Medical diagnostic report" \
  -F "file=@report.pdf"
```

**Query:**
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the diagnosis?", "session_id": "user_jwt_token"}'
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- MongoDB (local or cloud)
- NVIDIA API key (from [build.nvidia.com](https://build.nvidia.com/))
- Tavily API key (for web search — optional)

### Installation

```bash
# Clone
git clone https://github.com/nithin-developer/Adaptive-Rag.git
cd Adaptive-Rag-main

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# NVIDIA NIM (LLM + Embeddings)
NVIDIA_API_KEY=nvapi-your_nvidia_api_key_here

# Tavily Search (optional — for web search queries)
TAVILY_API_KEY=tvly-your_tavily_api_key_here

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=adaptive_rag

# JWT (optional — auto-generated if not set)
JWT_SECRET_KEY=your_long_random_secret_here
```

### Running the Application

**Terminal 1 — FastAPI backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Streamlit frontend:**
```bash
cd streamlit_app
streamlit run home.py
```

**Access:**
- Web interface: http://localhost:8501
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Usage

1. Open http://localhost:8501
2. Create an account → Sign in
3. Upload a document in the sidebar (PDF or TXT)
4. Ask questions in the chat — the system automatically routes to the right pipeline

---

## Configuration

### LLM & Embeddings

| Component | Model | Provider |
|-----------|-------|----------|
| **Chat LLM** | `mistralai/mistral-medium-3.5-128b` | NVIDIA NIM (OpenAI-compatible) |
| **Embeddings** | `nvidia/nv-embedqa-e5-v5` | NVIDIA NIM (asymmetric) |

Configured in `app/llms/openai.py` and `app/rag/retriever_setup.py`.

### Prompt Templates

All LLM prompts are in `app/config/prompts.yaml`:

| Prompt | Purpose |
|--------|---------|
| `system_prompt` | ReAct agent instructions |
| `classify_prompt` | Query classification (index / general / search) |
| `grading_prompt` | Document relevance scoring |
| `rewrite_prompt` | Query optimisation for re-retrieval |
| `generate_prompt` | Final answer generation |
| `verify_prompt` | Hallucination check |

### Query Routing

```
Incoming Query
    │
    ▼
query_analysis (classify)
    │
    ├── "index"   → retriever → grade → generate (or rewrite → retry)
    ├── "general"  → general_llm → END
    └── "search"   → web_search → generate → END
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Mistral 3.5 128B via NVIDIA NIM |
| **Embeddings** | NVIDIA NV-EmbedQA-E5-v5 |
| **Orchestration** | LangGraph |
| **Agent Framework** | LangChain (ReAct agent) |
| **Vector Store** | FAISS (in-memory) |
| **Web Framework** | FastAPI |
| **Frontend** | Streamlit |
| **Chat History** | MongoDB (Motor async driver) |
| **Auth** | JWT (python-jose) + SHA-256 password hashing (passlib) |
| **Web Search** | Tavily |
| **ASGI Server** | Uvicorn |

---

## Security Notes

- API keys stored in `.env` (never committed — listed in `.gitignore`)
- Passwords hashed with SHA-256 via passlib
- JWT tokens with configurable expiry (default 24h)
- API token validation on auth endpoints
- Add HTTPS and rate limiting for production deployments

---

## FAQ

**Q: Can I use a different LLM provider?**
A: Yes. Edit `app/llms/openai.py` — since it uses `ChatOpenAI`, any OpenAI-compatible endpoint works (OpenAI, Groq, Together, etc.).

**Q: Do I need the NVIDIA API key for both LLM and embeddings?**
A: Yes. The same `NVIDIA_API_KEY` is used for both the chat model and the embedding model via NVIDIA NIM.

**Q: How is conversation history stored?**
A: MongoDB stores all messages with session IDs. Each JWT token maps to a unique conversation.

**Q: Can I run without web search?**
A: Yes. If `TAVILY_API_KEY` is not set, queries classified as "search" will attempt to search but may fail gracefully.

**Q: What happens if I upload a new document?**
A: The `DynamicRetriever` automatically picks up new documents without restarting the server.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ using LangGraph, NVIDIA NIM, and FastAPI by Nithin