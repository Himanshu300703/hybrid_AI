# config_example.py — copy to config.py and fill with real values.
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# OPENAI_API_KEY = "OPENAI_API_KEY" # your OpenAI API key

PINECONE_API_KEY = "PINECONE_API_KEY" # your Pinecone API key
PINECONE_ENV = "us-east-1"   # example
PINECONE_INDEX_NAME = "vietnam-travel"
PINECONE_VECTOR_DIM = 384       # adjust to embedding model used (text-embedding-3-large ~ 3072? check your model); we assume 1536 for common OpenAI models — change if needed.
