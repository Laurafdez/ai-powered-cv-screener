# AI-Powered CV Screener

A full-stack AI application for screening and querying CVs using Retrieval-Augmented Generation (RAG). This project generates realistic CVs using AI, processes them through a RAG pipeline, and provides an interactive chat interface to query the CV database.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technical Details](#-technical-details)
- [API Endpoints](#-api-endpoints)
- [Architecture](#️-architecture)
- [License](#-license)

## 🎯 Overview

This project implements a complete AI-powered CV screening system with three main components:

1. **CV Generation Pipeline**: Generates 25-30 realistic, AI-generated CVs in PDF format
2. **RAG Backend**: Processes PDFs and makes them searchable using Amazon Knowledge Bases and Bedrock
3. **Chat Interface**: Web-based interface for querying CVs using natural language


## ✨ Features

### CV Generation
- ✅ Generates 25-30 unique, realistic CVs
- ✅ AI-generated professional photos
- ✅ Multi-language support (English & Spanish)
- ✅ Realistic content: work experience, skills, education, certifications
- ✅ Professional PDF formatting

### RAG Pipeline
- ✅ PDF text extraction
- ✅ Vector embeddings and semantic search
- ✅ Amazon Knowledge Bases integration
- ✅ Context-aware retrieval
- ✅ Source citations with page numbers

### Chat Interface
- ✅ Clean, intuitive web interface
- ✅ Natural language querying
- ✅ Role-based filtering (Security Engineer, Data Scientist, etc.)
- ✅ Response citations showing source CVs
- ✅ Real-time chat history



## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- AWS Account with access to:
  - AWS Bedrock (Amazon Nova Pro, Claude)
  - AWS S3 (for document storage)
  - Amazon Knowledge Bases (for RAG)

### Step 1: Install Dependencies

#### Using UV (Recommended)

```bash
# Install UV if you don't have it
pip install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install backend dependencies
cd backend
uv sync
```

#### Using pip

```bash
cd backend
# Install manually:
pip install fastapi uvicorn boto3 langchain-aws python-dotenv pypdf2
```

#### Additional Dependencies for CV Generator

```bash
pip install reportlab pillow requests
```

### Step 2: Configure Environment Variables

```bash
cd backend
cp env.example .env
```

Edit `.env` with your AWS credentials:

```bash
# AWS Bedrock (Required for CV Generator)
AWS_REGION=eu-central-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL=amazon.nova-pro-v1:0

# AWS S3 (Required for Backend)
S3_BUCKET_NAME=your-bucket-name
S3_PREFIX=documents/

# Amazon Knowledge Bases (Required for RAG)
KNOWLEDGE_BASE_ID=your-knowledge-base-id
KNOWLEDGE_BASE_ROLE_ARN=arn:aws:iam::...

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## ⚙️ Configuration

All configuration is centralized in `backend/config/settings.py`:

- **AWS Bedrock**: Region, credentials, model selection
- **AWS S3**: Bucket name, region, prefix
- **Amazon Knowledge Bases**: Knowledge Base ID, retrieval settings
- **API**: Host and port configuration
- **LLM**: Max tokens, temperature, top K parameters

## 📖 Usage

### 1. Generate CVs

```bash
cd backend
python generator_cvs_ia.py
```

This will:
- Read profiles from `profiles.json`
- Generate 30 CVs using Amazon Nova Pro
- Create professional PDFs in `backend/generated_cvs/`

**Customize generation:**

Edit `generator_cvs_ia.py` at the bottom:

```python
if __name__ == "__main__":
    generate_cvs_batch(
        count=30,              # Number of CVs to generate
        languages=['en', 'es'] # Available languages
    )
```

### 2. Upload CVs to Knowledge Base

Upload the generated CVs to your S3 bucket (configured in Knowledge Bases data source). The Knowledge Base will automatically:
- Extract text from PDFs
- Create vector embeddings
- Index the content for retrieval

### 3. Start Backend API

```bash
cd backend
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Start Frontend

```bash
cd frontend
streamlit run app.py
```

The UI will be available at `http://localhost:8501`

### 5. Use the Chat Interface

1. Navigate to the Chat page
2. Select a role category (optional filter)
3. Ask questions like:
   - "Who has experience with Python?"
   - "Which candidate graduated from UPC?"
   - "Summarize the profile of Jane Doe."
   - "Find all Security Engineers with Senior level experience"

## 📁 Project Structure

```
CV_assistant/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py           # Centralized configuration
│   ├── services/
│   │   ├── retriever_service.py  # RAG retrieval logic
│   │   ├── s3_service.py         # S3 upload service
│   │   └── bedrock_service.py    # Bedrock client service
│   ├── api/
│   │   ├── chat.py               # Chat endpoint
│   │   └── upload.py             # Upload endpoint
│   ├── schemas/
│   │   ├── chat.py               # Request/response models
│   │   └── upload.py
│   ├── utils/
│   │   └── utils.py              # Utility functions
│   ├── generated_cvs/            # Generated CVs (auto-created)
│   ├── generator_cvs_ia.py       # 🎯 CV Generator Script
│   ├── profiles.json             # 📋 Candidate Profiles
│   ├── main.py                   # FastAPI application
│   ├── pyproject.toml            # UV project configuration
│   ├── env.example               # Environment variables template
│   └── .env                      # Your environment variables
└── frontend/
    ├── app.py                    # Streamlit main app
    ├── config.py                 # Frontend configuration
    └── ui/
        ├── home.py               # Home page
        ├── upload.py             # Upload page
        └── chat.py               # Chat interface
```

## 🔧 Technical Details

### CV Generation Pipeline

**File**: `backend/generator_cvs_ia.py`

**Key Functions**:
- `generate_cv_content_with_nova()`: Uses Amazon Nova Pro to generate realistic CV content
- `generate_ai_photo()`: Generates professional photos using external APIs
- `create_cv_pdf()`: Creates formatted PDFs using ReportLab
- `generate_cvs_batch()`: Orchestrates batch generation

**Profile Format** (`profiles.json`):
```json
{
  "name": "John Doe",
  "gender": "male",
  "role": "Security Engineer",
  "level": "Junior"
}
```

### RAG Pipeline

**File**: `backend/services/retriever_service.py`

**Flow**:
1. User query received
2. Query sent to Amazon Knowledge Bases
3. Semantic search retrieves relevant CV chunks
4. Context assembled from retrieved chunks
5. Prompt constructed with context + query
6. Amazon Bedrock generates answer
7. Citations extracted and formatted
8. Response returned with citations

**Key Features**:
- Category-based filtering (by role)
- Relevance scoring
- Page-level citations
- Source file tracking

### Chat Interface

**File**: `frontend/ui/chat.py`

**Features**:
- Real-time chat history
- Role-based filtering
- Citation display
- Error handling



## 📝 API Endpoints

### POST `/api/chat`

Chat with RAG: searches Knowledge Bases and processes with Bedrock.

**Request:**
```json
{
  "message": "Who has experience with Python?",
  "category": "Data Scientist"
}
```

**Response:**
```json
{
  "response": "Based on the CVs found...\n\n**Citations:**\n**Citation 1**: [CV_001_John_Doe.pdf](url) - Page 1"
}
```

### POST `/api/upload`

Upload documents to S3 (PDF, DOCX, TXT, DOC).

**Request:** Form-data with `file` field

**Response:**
```json
{
  "message": "Document uploaded successfully to S3",
  "file_id": "uuid",
  "url": "https://bucket.s3.region.amazonaws.com/documents/uuid.pdf",
  "filename": "document.pdf"
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CV GENERATION LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  profiles.json ──┐                                               │
│                  │                                               │
│                  ├──> generator_cvs_ia.py                        │
│                  │    ├── Amazon Nova Pro (Bedrock)              │
│                  │    ├── AI Photo Generation APIs                │
│                  │    └── ReportLab PDF Generator                │
│                  │                                               │
│                  └──> 30 Realistic PDF CVs                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA PROCESSING LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PDF Upload ──> S3 Service ──> Amazon Knowledge Bases            │
│                                         │                        │
│                                         ├──> Vector Embeddings   │
│                                         ├──> Text Extraction     │
│                                         └──> Indexed Storage     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RAG BACKEND LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  FastAPI Backend                                                 │
│  ├── /api/chat ──> Retriever Service                             │
│  │                  ├── Query Knowledge Bases                    │
│  │                  ├── Retrieve Relevant CVs                    │
│  │                  └── Generate Context                          │
│  │                                                                │
│  └── /api/upload ──> S3 Service                                  │
│                      └── Upload & Index PDFs                      │
│                                                                   │
│  Amazon Bedrock (Claude/Nova Pro)                                │
│  └── Generate Answers with Citations                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Streamlit Web Interface                                         │
│  ├── Home Page                                                   │
│  ├── Upload CV Page                                              │
│  └── Chat Interface                                              │
│      ├── Role-based Filtering                                    │
│      ├── Natural Language Queries                                │
│      └── Response with Citations                                 │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 📄 License

This project is for internal use.

---

**Built with**: Python, FastAPI, Streamlit, Amazon Bedrock, Amazon Knowledge Bases, AWS S3, ReportLab
