# RAG Customer Support Chatbot

A powerful chatbot system that combines Retrieval-Augmented Generation (RAG) with Google's Gemini model to provide accurate responses based on insurance documents and Angel One financial support content.

## 🚀 Features

- **Dual Knowledge Source**: Processes both PDF/DOCX documents and web content from Angel One support
- **Advanced RAG Pipeline**: Optimized document retrieval with semantic search and ranking
- **Real-time Chat**: WebSocket support for instant responses
- **Source Attribution**: Clear citations to both document and web sources
- **Modern UI**: Clean, responsive interface with source highlighting

## 🏗️ Tech Stack

### Backend
- **Python 3.9+**: Core language
- **FastAPI**: High-performance API framework
- **LangChain**: RAG orchestration
- **ChromaDB**: Vector database for embeddings
- **HuggingFace Sentence Transformers**: For text embeddings (`BAAI/bge-small-en-v1.5`)
- **Google Gemini**: LLM for response generation

### Frontend
- **Next.js**: React framework
- **TypeScript**: Type-safe development
- **TailwindCSS**: Utility-first CSS
- **WebSockets**: Real-time communication

## 📋 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd rag-chatbot-system/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with the following content:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   API_KEY_REQUIRED=false
   VECTOR_DB_PATH=./data/vector_store
   DOCUMENTS_PATH=../documents
   PROCESSED_PATH=./data/processed
   WEB_CRAWL_BASE_URL=https://www.angelone.in/support
   WEB_CRAWL_MAX_PAGES=100
   ```

5. Run the web crawler to collect Angel One support content:
   ```bash
   python scripts/process_web_content.py --force-crawl
   ```

6. Process the insurance documents:
   ```bash
   python scripts/process_documents.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd rag-chatbot-system/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Create a `.env.local` file in the frontend directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_API_WS_URL=ws://localhost:8000
   ```

## 🚀 Running the Application

### Start the Backend

```bash
cd rag-chatbot-system/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

The API will be available at http://localhost:8000 with interactive docs at http://localhost:8000/docs

### Start the Frontend

```bash
cd rag-chatbot-system/frontend
npm run dev
# or
yarn dev
```

The frontend will be available at http://localhost:3000

## 🤖 Using the Chatbot

- Ask questions about insurance plans contained in the PDF documents
- Ask questions about Angel One's investment services, based on their support website
- View sources for each response and click to expand the exact content used
- Toggle the web content option to include/exclude Angel One support content

## 📊 System Architecture

```
┌────────────────┐       ┌───────────────────────────┐
│                │       │                           │
│   Next.js UI   │◄─────►│   FastAPI Backend         │
│                │       │                           │
└────────────────┘       └───────────┬───────────────┘
                                     │
                         ┌───────────▼───────────────┐
                         │                           │
                         │   RAG Pipeline            │
                         │                           │
                         └───────────┬───────────────┘
                                     │
                         ┌───────────▼───────────────┐
                         │                           │
         ┌───────────────┤   Vector Database         ├───────────────┐
         │               │                           │               │
         │               └───────────────────────────┘               │
┌────────▼─────────┐                                     ┌───────────▼─────────┐
│                  │                                     │                     │
│  Insurance Docs  │                                     │  Web Content        │
│  Embeddings      │                                     │  Embeddings         │
│                  │                                     │                     │
└──────────────────┘                                     └─────────────────────┘
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Google Gemini API for text generation
- HuggingFace for the embedding models
- LangChain for the RAG framework
- Angel One for their financial support content 