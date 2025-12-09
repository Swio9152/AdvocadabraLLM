"""
Core utilities and shared functionality for the AdvocaDabra backend.
Consolidates common patterns from SCR, PCR, and Embeddings modules.
"""

import os
import json
import faiss
import numpy as np
import joblib
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer


# =============================================================================
# CONFIGURATION & PATHS
# =============================================================================

class Config:
    """Centralized configuration management."""
    
    # Paths
    EMB_DIR = "./di_prime_embeddings"
    EMB_FILE = f"{EMB_DIR}/embeddings.npy"
    META_FILE = f"{EMB_DIR}/metadata.joblib"
    FAISS_FILE = f"{EMB_DIR}/faiss.index"
    CHECKPOINT_FILE = f"{EMB_DIR}/checkpoint.json"
    DI_PATH = "/Users/srinandanasarmakesapragada/Documents/data_raw/di_dataset.jsonl"
    
    # Model settings
    MODEL_NAME = "intfloat/e5-base"
    BATCH_SIZE = 64
    
    # Court prestige mapping
    COURT_PRESTIGE = {
        "supreme court": 5.0,
        "court of appeals": 4.0,
        "appellate division": 3.0,
        "circuit court": 2.5,
        "district court": 1.5,
        "trial court": 1.0,
    }


# =============================================================================
# RESOURCE MANAGER
# =============================================================================

class ResourceManager:
    """Manages loading and caching of shared resources."""
    
    def __init__(self):
        self._model = None
        self._index = None
        self._metadata = None
        self._cases = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load and cache the sentence transformer model."""
        if self._model is None:
            print(f"Loading embedding model ({Config.MODEL_NAME})...")
            self._model = SentenceTransformer(Config.MODEL_NAME)
        return self._model
    
    @property
    def index(self) -> faiss.Index:
        """Lazy load and cache the FAISS index."""
        if self._index is None:
            print("Loading FAISS index...")
            self._index = faiss.read_index(Config.FAISS_FILE)
        return self._index
    
    @property
    def metadata(self) -> Any:
        """Lazy load and cache metadata."""
        if self._metadata is None:
            print("Loading metadata...")
            self._metadata = joblib.load(Config.META_FILE)
        return self._metadata
    
    @property
    def cases(self) -> List[Dict[str, Any]]:
        """Lazy load and cache cases from DI dataset."""
        if self._cases is None:
            print("Loading DI dataset...")
            self._cases = []
            with open(Config.DI_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        self._cases.append(json.loads(line))
                    except:
                        pass
        return self._cases


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def make_text(case: Dict[str, Any], max_length: int = 10000) -> str:
    """Extract text content from a case dictionary."""
    for field in ["summary", "case_summary", "facts", "raw_text"]:
        if field in case and case[field]:
            return " ".join(case[field].split())[:max_length]
    return ""


def court_score(text: Optional[str]) -> float:
    """Calculate court prestige score based on text content."""
    if not text:
        return 0.0
    
    text = text.lower()
    score = 0.0
    for court_type, prestige in Config.COURT_PRESTIGE.items():
        if court_type in text:
            score = max(score, prestige)
    return score


def load_checkpoint() -> Dict[str, Any]:
    """Load processing checkpoint if it exists."""
    if not os.path.exists(Config.CHECKPOINT_FILE):
        return {"done": 0}
    try:
        with open(Config.CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"done": 0}


def save_checkpoint(state: Dict[str, Any]) -> None:
    """Save processing checkpoint."""
    # Convert numpy int64 to regular int for JSON serialization
    state = {k: int(v) if isinstance(v, (np.integer, np.int64)) else v 
             for k, v in state.items()}
    with open(Config.CHECKPOINT_FILE, "w") as f:
        json.dump(state, f)


def normalize_query(query_text: str) -> str:
    """Normalize query text for E5 model (add query prefix)."""
    return "query: " + query_text


def encode_and_normalize(model: SentenceTransformer, text: str) -> np.ndarray:
    """Encode text and normalize for FAISS similarity search."""
    embedding = model.encode(text, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(embedding.reshape(1, -1))
    return embedding


# =============================================================================
# GLOBAL RESOURCE INSTANCE
# =============================================================================

# Singleton instance for shared access
resources = ResourceManager()
