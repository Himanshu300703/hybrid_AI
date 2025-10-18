import json
from typing import List, Dict
from pinecone import Pinecone
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import ollama
import config
import time
from functools import lru_cache

# ===== CONFIGURATION =====
TOP_K = 5
INDEX_NAME = config.PINECONE_INDEX_NAME
OLLAMA_MODEL = "orca-mini"

# ===== CACHE & PERFORMANCE =====
query_cache: Dict = {}  # Simple in-memory cache for embeddings
MAX_CACHE_SIZE = 100

# ===== INITIALIZE CLIENTS =====
pc = Pinecone(api_key=config.PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

driver = None
try:
    driver = GraphDatabase.driver(
        config.NEO4J_URI, 
        auth=(config.NEO4J_USER, config.NEO4J_PASSWORD),
        connection_timeout=5
    )
    with driver.session() as session:
        session.run("RETURN 1")
    print("Neo4j connected successfully")
except Exception as e:
    print(f"Neo4j connection failed: {e}")
    driver = None

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ===== CACHING LAYER =====

def get_cached_embedding(text: str) -> List[float]:
    """Get embedding with caching to avoid recomputation."""
    if text in query_cache:
        return query_cache[text]
    
    embedding = embedder.encode([text])[0].tolist()
    
    # Simple LRU-like cache management
    if len(query_cache) >= MAX_CACHE_SIZE:
        oldest_key = next(iter(query_cache))
        del query_cache[oldest_key]
    
    query_cache[text] = embedding
    return embedding

# ===== HELPER FUNCTIONS =====

def embed_text(text: str) -> List[float]:
    """Generate embedding for text query with caching."""
    return get_cached_embedding(text)

def pinecone_query(query_text: str, top_k=TOP_K) -> List:
    """Retrieve top semantic matches from Pinecone."""
    vec = embed_text(query_text)
    res = index.query(vector=vec, top_k=top_k, include_metadata=True)
    print(f"Pinecone found {len(res['matches'])} semantic matches")
    return res.get("matches", [])

def fetch_graph_context(node_ids: List[str]) -> List:
    """Fetch related nodes from Neo4j with optimized queries."""
    if driver is None:
        print("📊 Neo4j unavailable - skipping graph enrichment")
        return []
    
    facts = []
    try:
        with driver.session() as session:
            # Batch query for all nodes at once (more efficient)
            for nid in node_ids:
                query = (
                    "MATCH (n:Entity {id:$nid})-[r]-(m:Entity) "
                    "RETURN type(r) AS rel, labels(m) AS labels, m.id AS id, "
                    "m.name AS name, m.type AS type, m.description AS description "
                    "LIMIT 10"
                )
                records = session.run(query, nid=nid)
                for record in records:
                    facts.append({
                        "source": nid,
                        "rel": record["rel"],
                        "target_id": record["id"],
                        "target_name": record["name"] or record["id"],
                        "target_desc": (record["description"] or "")[:300],
                        "target_type": record["type"],
                        "labels": record["labels"]
                    })
    except Exception as e:
        print(f"Neo4j query error: {e}")
    
    print(f"Neo4j retrieved {len(facts)} relationships")
    return facts

def summarize_top_nodes(matches: List) -> str:
    """Summarize top semantic matches for quick insights."""
    if not matches:
        return "No matches found."
    
    summary_lines = []
    for i, match in enumerate(matches[:3], 1):
        meta = match.get("metadata", {})
        name = meta.get("name", "Unknown")
        place_type = meta.get("type", "Unknown")
        summary_lines.append(f"{i}. {name} ({place_type})")
    
    return " | ".join(summary_lines)

def build_context_prompt(user_query: str, pinecone_matches: List, graph_facts: List) -> str:
    """Build rich context prompt with chain-of-thought reasoning."""
    
    # Format vector search results
    vec_context_lines = []
    for i, match in enumerate(pinecone_matches[:5], 1):
        meta = match.get("metadata", {})
        name = meta.get("name", "Unknown")
        place_type = meta.get("type", "Unknown")
        city = meta.get("city", "")
        score = match.get("score", 0)
        vec_context_lines.append(
            f"{i}. {name} ({place_type}) in {city} [relevance: {score:.2f}]"
        )
    
    # Format graph relationships
    graph_lines = []
    for fact in graph_facts[:10]:
        source = fact["source"].replace("_", " ").title()
        target = fact["target_name"].replace("_", " ").title()
        rel = fact["rel"].replace("_", " ").lower()
        graph_lines.append(f"- {source} is {rel} {target}")
    
    # Enhanced prompt with chain-of-thought reasoning
    prompt = f"""You are a knowledgeable travel planner for Vietnam with expertise in creating personalized itineraries.

USER QUERY: {user_query}

STEP 1 - SEMANTIC SEARCH RESULTS (from vector database):
{chr(10).join(vec_context_lines) if vec_context_lines else "No results found"}

STEP 2 - RELATED LOCATIONS & CONNECTIONS (from knowledge graph):
{chr(10).join(graph_lines) if graph_lines else "No relationships found"}

STEP 3 - REASONING:
Analyze the search results and relationships. Consider:
- Geographic proximity and travel logistics
- Travel themes (romance, adventure, culture, nature)
- Best time/duration for each location
- How locations connect logically for an itinerary

STEP 4 - RESPONSE:
Create a helpful, specific travel recommendation. 
- If creating an itinerary, organize by days with specific locations from results
- Mention logistics (how to travel between locations)
- Cite specific locations from the results
- Be concise (2-3 paragraphs max)

Your response:"""
    
    return prompt

def call_ollama_chat(prompt_text: str) -> str:
    """Call Ollama API for chat completion."""
    try:
        start_time = time.time()
        print("Calling orca-mini model...", end=" ", flush=True)
        
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt_text,
            stream=False,
            options={
                "temperature": 0.7,
                "top_p": 0.9,
            }
        )
        
        elapsed = time.time() - start_time
        print(f"(completed in {elapsed:.2f}s)")
        
        return response.get("response", "").strip()
    except Exception as e:
        print(f"\nOllama error: {e}")
        return f"Error: {str(e)}"

def generate_response(prompt_text: str) -> str:
    """Generate response using Ollama with timing."""
    return call_ollama_chat(prompt_text)

# ===== MAIN CHAT LOOP =====

def interactive_chat():
    print("\n" + "="*70)
    print("HYBRID TRAVEL ASSISTANT FOR VIETNAM")
    print("="*70)
    print("Components:")
    print("- Vector Search: Pinecone (semantic understanding)")
    print("- Knowledge Graph: Neo4j (location relationships)")
    print("- LLM: Orca-Mini (local, low VRAM)")
    print("- Optimizations: Caching, chain-of-thought, batched queries")
    print("\nType 'exit' to quit | Type 'cache' to see cache stats\n")
    
    query_count = 0
    
    while True:
        query = input("Enter your travel question: ").strip()
        
        if query.lower() == "exit" or query.lower() == "quit":
            print("Goodbye!")
            break
        
        if query.lower() == "cache":
            print(f"Cache stats: {len(query_cache)} embeddings cached")
            continue
        
        if not query:
            print("Please enter a valid query.\n")
            continue
        
        query_count += 1
        print(f"\n[Query #{query_count}] Processing...\n")
        
        try:
            # Step 1: Vector search
            start = time.time()
            matches = pinecone_query(query, top_k=TOP_K)
            pinecone_time = time.time() - start
            
            # Show quick summary
            summary = summarize_top_nodes(matches)
            print(f"   Quick summary: {summary}")
            
            # Step 2: Graph enrichment
            start = time.time()
            match_ids = [m["id"] for m in matches]
            graph_facts = fetch_graph_context(match_ids)
            graph_time = time.time() - start
            
            # Step 3: Build prompt
            prompt = build_context_prompt(query, matches, graph_facts)
            
            # Step 4: Generate response
            print(f"Generating response with orca-mini...", flush=True)
            start = time.time()
            answer = generate_response(prompt)
            llm_time = time.time() - start
            
            # Step 5: Display with timing
            print("\n" + "="*70)
            print("RESPONSE:")
            print("="*70)
            print(answer)
            print("="*70)
            print(f"\nTiming: Pinecone={pinecone_time:.2f}s | Neo4j={graph_time:.2f}s | LLM={llm_time:.2f}s")
            print(f"Cache: {len(query_cache)} embeddings cached\n")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

# ===== MAIN =====

if __name__ == "__main__":
    try:
        interactive_chat()
    except KeyboardInterrupt:
        print("\n\nSession ended by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.close()