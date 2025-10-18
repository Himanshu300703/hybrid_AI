# 🌍 Hybrid AI Travel Assistant for Vietnam

A **production-ready AI system** combining **semantic search (Pinecone)**, **knowledge graphs (Neo4j)**, and **local LLMs (Orca-Mini)** to generate intelligent, contextual **Vietnam travel itineraries** — entirely offline.

---

## ✨ Features

- 🧠 **Semantic Search:** Understands natural language queries like “romantic”, “adventure”, “budget-friendly”
- 🗺️ **Knowledge Graph:** Uses Neo4j to relate cities, attractions, and activities
- 💻 **Local LLM (Orca-Mini):** Runs locally on 2 GB VRAM via Ollama — no API costs
- 🔗 **Hybrid Intelligence:** Fuses vector semantics with graph structure
- ⚡ **Optimized Performance:** Embedding caching, batch queries, and async-ready
- 🛡️ **Graceful Degradation:** Works even if a service (e.g., Neo4j) is offline
- 🔄 **Forward Compatible:** Easily switch between local and cloud LLMs

## 🛠️ Tech Stack

- 🧬 Embeddings: SentenceTransformer (all-MiniLM-L6-v2, 384 dim)
- 📊 Vector DB: Pinecone (Serverless GCP us-east-1)
- 🗂️ Graph DB: Neo4j (Community Edition / Docker)
- 🤖 LLM: Orca-Mini (2 GB VRAM) via Ollama
- 🐍 Language: Python 3.8+
- 📦 Frameworks: transformers, sentence-transformers, neo4j-driver, pinecone-client

## 📈 Improvements Implemented

- 💾 Embedding Cache → faster repeated queries
- ⚙️ Async Retrieval → parallel Pinecone + Neo4j
- 📝 Prompt Engineering → concise, structured itineraries
- 🚨 Graceful Error Handling → continues even if a component fails

---

## 🏗️ System Architecture
```
User Query
↓
SentenceTransformer (encode to embedding)
↓
Pinecone (semantic search)
↓
Neo4j (relationship enrichment)
↓
Ollama Orca-Mini (generation)
↓
Final Itinerary Response
```

---

## 🚀 Quick Start

### Prerequisites
```
# Core Dependencies
pinecone-client>=3.0.0
neo4j>=5.0.0
sentence-transformers>=2.2.0
ollama>=0.1.0

# Utilities
tqdm>=4.65.0
requests>=2.31.0

# For graph visualization
pyvis>=0.3.2
networkx>=3.0
```

## 📥 Clone & Setup

```bash
git clone https://github.com/Himanshu300703/hybrid_AI
cd hybrid_AI
python -m venv venv
venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
```

### 1. Edit config.py:
```
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
PINECONE_API_KEY = "PINECONE_API_KEY" # your Pinecone API key
PINECONE_ENV = "us-east-1"   # example
PINECONE_INDEX_NAME = "vietnam-travel"
PINECONE_VECTOR_DIM = 384 
```

### 2. Load Data
```
python load_to_neo4j.py      # Create graph
python pinecone_upload.py    # Upload embeddings
```

### 3. Run Ollama
```
ollama serve
```
Keep this terminal open.

### 4. Start the Chat Assistant
```
python hybrid_chat.py
```

### 5. Example:

Enter your travel question: ```create a romantic 4 day itinerary for Vietnam```

Output Screenshot:

<img width="1545" height="746" alt="image" src="https://github.com/user-attachments/assets/bf6e196d-35be-485c-96fe-5e1272ec12ae" />
