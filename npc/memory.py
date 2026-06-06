import chromadb
from chromadb.config import Settings
import hashlib
import os

# Persist to disk so memory survives restarts
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "memory_store")

client = chromadb.PersistentClient(path=MEMORY_PATH)
collection = client.get_or_create_collection(
    name="npc_memory",
    metadata={"hnsw:space": "cosine"}
)


def _make_id(player_id: str, text: str) -> str:
    """Stable unique ID for a memory entry"""
    return hashlib.md5(f"{player_id}:{text}".encode()).hexdigest()


def save_memory(player_id: str, role: str, content: str):
    """Store a single conversation turn in ChromaDB"""
    doc_id = _make_id(player_id, content)
    collection.upsert(
        ids=[doc_id],
        documents=[content],
        metadatas=[{"player_id": player_id, "role": role}]
    )


def recall_memories(player_id: str, query: str, n_results: int = 4) -> list[str]:
    """Retrieve the most relevant past memories for this player"""
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"player_id": player_id}
        )
        return results["documents"][0] if results["documents"] else []
    except Exception:
        return []


def get_all_memories(player_id: str) -> list[str]:
    """Pull all stored memories for a player (for debug)"""
    try:
        results = collection.get(where={"player_id": player_id})
        return results["documents"]
    except Exception:
        return []