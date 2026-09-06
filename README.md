# 🎯 Student Placement Interview AI

An AI-powered mock interview system built for placement preparation using **Groq LLM**, **RAG (Retrieval-Augmented Generation)**, **MCP (Model Context Protocol)**, and a full-stack **FastAPI + Streamlit** application.

---

## 🏗️ Architecture

```
placement-interview-ai/
├── main.py                    ← FastAPI app entry point
├── requirements.txt
├── .env                       ← Your API keys (never commit this!)
├── config/
│   ├── settings.py            ← All config via environment variables
│   └── logging_config.py
├── app/
│   ├── agents/
│   │   ├── groq_client.py     ← Groq LLM wrapper
│   │   ├── interview_agent.py ← AI interview conductor
│   │   └── feedback_agent.py  ← Resume & study plan feedback
│   ├── rag/
│   │   ├── document_loader.py ← PDF/DOCX/TXT loader + chunking
│   │   ├── embeddings.py      ← HuggingFace sentence-transformers
│   │   ├── vector_store.py    ← ChromaDB / FAISS vector store
│   │   └── retriever.py       ← Context retrieval for RAG
│   ├── mcp/
│   │   └── mcp_server.py      ← MCP tool server (5 tools)
│   ├── models/
│   │   ├── schemas.py         ← Pydantic request/response models
│   │   └── session_manager.py ← Interview session management
│   ├── api/
│   │   ├── routes.py          ← All REST endpoints
│   │   └── dependencies.py    ← FastAPI dependency injection
│   └── utils/
│       └── helpers.py         ← Utility functions
├── frontend/
│   └── app.py                 ← Streamlit UI
├── data/
│   ├── resumes/               ← Upload student resumes here
│   ├── job_descriptions/      ← Upload JDs here
│   └── question_bank/         ← Question bank files
└── vector_store/              ← Auto-generated vector DB
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd placement-interview-ai
pip install -r requirements.txt
```

### Step 2: Configure Environment

Your `.env` file is already set up. Make sure `GROQ_API_KEY` is filled in.

Get a free Groq API key at: https://console.groq.com

### Step 3: Start the Backend API

```bash
python main.py
```

API will be available at: http://localhost:8000
API Docs (Swagger): http://localhost:8000/docs

### Step 4: Start the Frontend

Open a **new terminal** and run:

```bash
streamlit run frontend/app.py
```

Frontend will be available at: http://localhost:8501

---

## 🤖 Features

### Mock Interview
- AI conducts a full placement-style interview
- Questions generated using RAG from your resume & JD
- Real-time answer evaluation with scoring (1-10)
- Strengths, improvements, and hints after each answer
- Final comprehensive report

### RAG Pipeline
- Upload resumes (PDF/DOCX/TXT) to `data/resumes/`
- Upload JDs to `data/job_descriptions/`
- Questions are automatically personalized from your documents

### MCP Tools (5 available)
| Tool | Description |
|------|-------------|
| `search_interview_questions` | Search question bank by topic |
| `search_resume` | Semantic search through resumes |
| `search_job_description` | Search JDs for skills/requirements |
| `get_interview_tip` | Quick tips for any topic |
| `evaluate_answer_quick` | Fast answer scoring |

### Resume Analyzer
- Paste your resume + JD
- Get AI feedback, score, missing keywords

### Study Plan Generator
- Input weak topics
- Get a personalized N-day study plan

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/interview/start` | Start interview session |
| POST | `/api/v1/interview/answer` | Submit answer |
| GET | `/api/v1/interview/{id}/report` | Final report |
| GET | `/api/v1/mcp/tools` | List MCP tools |
| POST | `/api/v1/mcp/call` | Call MCP tool |
| POST | `/api/v1/feedback/resume` | Resume feedback |
| POST | `/api/v1/feedback/study-plan` | Study plan |

Full interactive docs at: **http://localhost:8000/docs**

---

## ⚙️ Configuration (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | **Required** — Get from console.groq.com |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model |
| `INTERVIEW_DIFFICULTY` | `medium` | easy/medium/hard |
| `MAX_INTERVIEW_QUESTIONS` | `10` | Questions per session |
| `VECTOR_STORE_TYPE` | `chroma` | chroma/faiss |
| `RAG_TOP_K` | `5` | Documents retrieved per query |

---

## 🧑‍💻 Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq API (Llama 3.3 70B) |
| RAG | LangChain + ChromaDB |
| Embeddings | HuggingFace sentence-transformers |
| MCP | Custom MCP tool server |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Validation | Pydantic v2 |

---

## 📝 Adding Your Own Data

1. **Resume**: Put your resume PDF/DOCX/TXT in `data/resumes/`
2. **Job Description**: Put target JD in `data/job_descriptions/`
3. **Questions**: Add custom questions in `data/question_bank/`
4. Restart the backend — RAG will auto-index new files

---

Built with ❤️ for placement preparation | Powered by Groq AI
