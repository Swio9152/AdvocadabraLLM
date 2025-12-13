import faiss
import numpy as np
import joblib
import json
from sentence_transformers import SentenceTransformer

EMB_DIR = "./di_prime_embeddings"
EMB_FILE = f"{EMB_DIR}/embeddings.npy"
META_FILE = f"{EMB_DIR}/metadata.joblib"
FAISS_FILE = f"{EMB_DIR}/faiss.index"

DI_PATH = "/Users/srinandanasarmakesapragada/Documents/data_raw/di_dataset.jsonl"

print("Loading FAISS index...")
index = faiss.read_index(FAISS_FILE)

print("Loading metadata...")
metadata = joblib.load(META_FILE)

print("Loading DI...")
cases = []
with open(DI_PATH, "r", encoding="utf-8") as f:
    for line in f:
        try:
            cases.append(json.loads(line))
        except:
            pass

print("Loading embedding model (e5-base)...")
model = SentenceTransformer("intfloat/e5-base")   # <-- FIXED


def retrieve_similar_cases(query_text, k=10):
    """Return top-k UNIQUE similar cases (no duplicate case_ids)."""

    # e5 recommends using "query: " prefix
    query_text = "query: " + query_text

    # Encode and normalize
    query_emb = model.encode(query_text, convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_emb.reshape(1, -1))

    # Fetch extra neighbors to ensure we get k unique case_ids
    # Increase search limit significantly to handle duplicates
    SEARCH_LIMIT = max(k * 20, 200)

    distances, indices = index.search(query_emb.reshape(1, -1), SEARCH_LIMIT)

    results = []
    seen_ids = set()

    for dist, idx in zip(distances[0], indices[0]):
        # Check for valid index
        if idx < 0 or idx >= len(metadata):
            continue
            
        try:
            cid = metadata[idx]["case_id"]
        except (KeyError, IndexError):
            continue

        # skip duplicates
        if cid in seen_ids:
            continue

        seen_ids.add(cid)

        try:
            case = cases[idx]
            sample = case.get("summary") or case.get("raw_text", "")

            results.append({
                "case_id": cid,
                "score": float(dist),   # cosine similarity (because of IP index + L2 norm)
                "text_sample": sample,
                "title": case.get("title", ""),
                "court": case.get("court", ""),
                "date": case.get("date", "")
            })

            if len(results) == k:
                break
        except (IndexError, KeyError):
            continue

    return results


def recall_at_k(results, relevant_case_ids):
    retrieved_case_ids = {r['case_id'] for r in results}
    relevant_set = set(relevant_case_ids)
    intersection = retrieved_case_ids & relevant_set
    if len(relevant_set) == 0:
        return 0.0
    return len(intersection) / len(relevant_set)


def evaluate_scr(eval_file, k=10):
    with open(eval_file, 'r') as f:
        eval_data = json.load(f)
    
    recalls = []
    for item in eval_data:
        query = item['query']
        relevant_ids = item['relevant_case_ids']
        
        results = retrieve_similar_cases(query, k=k)
        recall = recall_at_k(results, relevant_ids)
        recalls.append(recall)
        
        print(f"Query: {query[:50]}...")
        print(f"Recall@{k}: {recall:.4f}")
        print()
    
    mean_recall = sum(recalls) / len(recalls) if recalls else 0.0
    return mean_recall


if __name__ == "__main__":
    eval_file = "scr_eval.json"
    k = 10
    
    mean_recall = evaluate_scr(eval_file, k=k)
    print(f"Mean Recall@{k}: {mean_recall:.4f}")