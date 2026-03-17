.

🚀 Agentic AI Video Compliance Engine

An agentic, multi-modal compliance system that audits video content (e.g., YouTube) against structured regulatory guidelines (PDFs) and produces a deterministic PASS / FAIL decision.

This system leverages a Retrieval-Augmented Generation (RAG) architecture with Azure-native services and a LangGraph-based multi-agent workflow.

🧠 Problem Statement

Brands and regulators define content policies in PDF documents, but manual video auditing is:

⏳ Slow

💸 Expensive

❌ Inconsistent

📉 Not scalable

✅ Solution

This system automates compliance validation by:

Extracting transcripts + OCR from videos

Indexing policy PDFs into a vector database

Running a multi-agent audit workflow

Producing a structured compliance verdict

🏗 Architecture Overview
🔄 Agentic Workflow (LangGraph DAG)
START → Indexer Agent → Auditor Agent → END
🧩 Agents
Agent	Role
Indexer Agent	Extracts transcript, OCR text, and metadata from video
Auditor Agent	Uses RAG to validate content against compliance guidelines
☁ Azure Services Used
Service	Purpose
Azure Blob Storage	Temporary video storage
Azure Video Indexer	Transcript + OCR extraction
Azure AI Search	Vector database for guidelines
Azure OpenAI	LLM reasoning + embeddings
Azure Application Insights	Logging & monitoring
LangSmith	LLM tracing & observability
🔎 End-to-End Flow
YouTube URL
   ↓
Video Download
   ↓
Azure Blob Storage
   ↓
Azure Video Indexer (Transcript + OCR)
   ↓
Extracted Text
   ↓
Embeddings (Azure OpenAI)
   ↓
Azure AI Search (Vector Index)
   ↓
Auditor Agent (RAG Reasoning)
   ↓
Compliance Verdict (PASS / FAIL)


📂 Project Structure
ComplianceQAPipeline/
│
├── backend/
│   ├── data/                         # Policy PDFs
│   │   ├── 1001a-influencer-guide-508_1.pdf
│   │   └── youtube-ad-specs.pdf
│   │
│   ├── scripts/
│   │   └── index_documents.py        # PDF → Embeddings → Azure AI Search
│   │
│   ├── src/
│   │   ├── api/
│   │   │   ├── server.py             # FastAPI server
│   │   │   └── telemetry.py          # Application Insights
│   │   │
│   │   ├── graph/
│   │   │   ├── nodes.py              # Agent logic (Indexer + Auditor)
│   │   │   ├── state.py              # Shared state schema
│   │   │   └── workflow.py           # LangGraph DAG definition
│   │   │
│   │   └── services/
│   │       └── video_indexer.py      # Azure Video Indexer integration
│   │
│   └── tests/
│
├── main.py                           # CLI entry point
├── requirements.txt
├── .env
├── .env.example
├── Project2_Langgraph_Architecture.png
└── README.md


⚙️ Setup Instructions
1️⃣ Clone the Repository

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure Environment Variables

Copy:

.env.example → .env

Fill in:

# --- AZURE STORAGE ---
AZURE_STORAGE_CONNECTION_STRING=""

# --- AZURE OPENAI ---
AZURE_OPENAI_API_KEY=""
AZURE_OPENAI_ENDPOINT=""
AZURE_OPENAI_API_VERSION=""
AZURE_OPENAI_CHAT_DEPLOYMENT=""
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=""

# --- AZURE AI SEARCH ---
AZURE_SEARCH_ENDPOINT=""
AZURE_SEARCH_API_KEY=""
AZURE_SEARCH_INDEX_NAME=""

# --- AZURE VIDEO INDEXER ---
AZURE_VI_NAME=""
AZURE_VI_LOCATION=""
AZURE_VI_ACCOUNT_ID=""
AZURE_SUBSCRIPTION_ID=""
AZURE_RESOURCE_GROUP=""

# --- OBSERVABILITY ---
APPLICATIONINSIGHTS_CONNECTION_STRING=""

# --- LANGSMITH ---
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=""
LANGCHAIN_API_KEY=""
LANGCHAIN_PROJECT=""


▶️ Running the System
📌 Step 1: Index Policy PDFs
python backend/scripts/index_documents.py
📌 Step 2: Run CLI Mode
python main.py
📌 Step 3 (Optional): Run FastAPI Server
uvicorn backend.src.api.server:app --reload
📊 Example Output
Video ID: abc123
Matched Guideline: Section 4.2 – Misleading Claims
Decision: ❌ FAIL
Reason: Detected promotional claim violates approved wording.
Confidence: 0.87
🧠 Technical Highlights

✅ Agentic orchestration using LangGraph

🎥 Multi-modal ingestion (audio + visual + text)

🔎 Vector search with Azure AI Search

🧠 RAG-based compliance reasoning

☁ Fully Azure-native architecture

📊 Observability via LangSmith + App Insights

🎯 Deterministic compliance decisioning using structured prompts

🔮 Future Improvements

🌐 Web dashboard UI

👨‍⚖️ Human-in-the-loop review system

⚡ Real-time moderation API

📈 Advanced confidence scoring

📚 Multi-policy evaluation engine
