# config_example.py — copy to config.py and fill with real values.
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Himanshu@03"

OPENAI_API_KEY = "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" # your OpenAI API key

PINECONE_API_KEY = "pcsk_4WFvEY_9QnQqGNGZoeqKHAKVr1qDPrzRNcdPSuXAiNhrJYrCpPTq5zMAsWjfWyMMENghqy" # your Pinecone API key
PINECONE_ENV = "us-east-1"   # example
PINECONE_INDEX_NAME = "vietnam-travel"
PINECONE_VECTOR_DIM = 384       # adjust to embedding model used (text-embedding-3-large ~ 3072? check your model); we assume 1536 for common OpenAI models — change if needed.
