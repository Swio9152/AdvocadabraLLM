import faiss
import numpy as np
import joblib
import json
from sentence_transformers import SentenceTransformer

# ---------------------------------------------
# PATHS
# ---------------------------------------------
EMB_DIR = "/Users/uditkandi/project 3-1/di_prime_embeddings"
META_FILE = f"{EMB_DIR}/metadata.joblib"
FAISS_FILE = f"{EMB_DIR}/faiss.index"
DI_PATH = "/Users/uditkandi/project 3-1/di_dataset2.jsonl"

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

print("Loading embedding model (E5-base)...")
model = SentenceTransformer("intfloat/e5-base")

# ---------------------------------------------
# COURT PRESTIGE MAP
# ---------------------------------------------
COURT_PRESTIGE = {
    "supreme court": 5.0,
    "court of appeals": 4.0,
    "appellate division": 3.0,
    "circuit court": 2.5,
    "district court": 1.5,
    "trial court": 1.0,
}

def court_score(text):
    text = text.lower()
    score = 0.0
    for court, w in COURT_PRESTIGE.items():
        if court in text:
            score += w
    return score


# ---------------------------------------------
# BAD CASE FILTER: Remove procedural junk
# ---------------------------------------------
BAD_PHRASES = [
    "motion denied",
    "motion to dismiss",
    "appeal dismissed",
    "appeal denied",
    "motion for leave",
    "summary order",
    "order affirmed",
    "order reversed",
    "reargument denied",
    "dismissed on procedural grounds",
    "petition denied",
    "leave to appeal denied",
]

def is_procedural_case(text):
    t = text.lower()
    return any(p in t for p in BAD_PHRASES)


# ---------------------------------------------
# KEYWORD DEPTH SCORE (reasoning strength)
# ---------------------------------------------
DEPTH_KEYWORDS = [
    ("opinion of the court", 4.0),
    ("we hold", 2.5),
    ("the issue is", 2.0),
    ("the question before the court", 2.0),
    ("in this action", 1.5),
    ("as a matter of law", 1.5),
    ("reasoning", 2.0),
    ("analysis", 1.5),
]

def reasoning_depth(text):
    t = text.lower()
    score = 0
    for key, w in DEPTH_KEYWORDS:
        if key in t:
            score += w
    return score


# ---------------------------------------------
# MAIN PCR FUNCTION
# ---------------------------------------------
def recommend_precedents(query_text, k=10):
    # E5 requires prefix
    query_text = "query: " + query_text.strip()

    query_emb = model.encode(query_text, convert_to_numpy=True).astype("float32")
    query_emb = np.expand_dims(query_emb, 0)

    SEARCH_LIMIT = 200  # fetch MANY candidates

    distances, indices = index.search(query_emb, SEARCH_LIMIT)

    candidates = []
    seen_ids = set()

    for dist, idx in zip(distances[0], indices[0]):
        case = cases[idx]
        cid = case.get("case_id")
        raw = case.get("raw_text", "")

        # remove dupes
        if cid in seen_ids:
            continue
        seen_ids.add(cid)

        # ----------------------------
        # HARD FILTERS
        # ----------------------------
        if len(raw) < 800:
            continue  # too short = procedural junk

        if is_procedural_case(raw):
            continue  # remove orders

        # ----------------------------
        # FEATURE SCORES
        # ----------------------------
        sim = float(dist)
        court_s = court_score(raw)
        depth_s = reasoning_depth(raw)

        # extra keyword scoring
        kw_s = 1.0 if "trademark" in raw.lower() else 0.0

        # FINAL SCORE
        final = (
            sim * 1.0          # core relevance
            + court_s * 0.20   # authority
            + depth_s * 0.15   # reasoning quality
            + kw_s * 0.10      # topic alignment
        )

        candidates.append({
            "case_id": cid,
            "similarity": sim,
            "precedent_strength": court_s,
            "reasoning_depth": depth_s,
            "keyword_bonus": kw_s,
            "final_score": final,
            "sample": raw[:400]
        })

    # rank by final score
    candidates = sorted(candidates, key=lambda x: x["final_score"], reverse=True)

    return candidates[:k]
# ---------------------------------------------
# FINAL PRECEDENT SELECTOR (ONE CASE + EXPLANATION)
# ---------------------------------------------
def find_best_precedent(query_text):
    """Return ONE final precedent case with an explanation."""
    
    top_cases = recommend_precedents(query_text, k=10)
    
    if not top_cases:
        return {
            "precedent_case": None,
            "explanation": "No suitable precedent found after applying filters."
        }

    best = top_cases[0]

    cid = best["case_id"]
    sim = best["similarity"]
    court = best["precedent_strength"]
    depth = best["reasoning_depth"]
    topic = best["keyword_bonus"]
    sample = best["sample"]

    explanation_lines = []
    explanation_lines.append(f"Case {cid} is selected as the strongest precedent because:")

    # authority
    if court >= 4:
        explanation_lines.append(f"- It originates from a highly authoritative court (score {court:.2f}).")
    elif court > 0:
        explanation_lines.append(f"- It comes from a moderately authoritative court (score {court:.2f}).")
    else:
        explanation_lines.append(f"- Although court authority is low ({court:.2f}), other factors compensate.")

    # reasoning strength
    if depth >= 3:
        explanation_lines.append(f"- The case contains substantial judicial reasoning (depth {depth:.2f}).")
    elif depth > 0:
        explanation_lines.append(f"- The case includes some relevant legal reasoning (depth {depth:.2f}).")
    else:
        explanation_lines.append(f"- It lacks explicit reasoning phrases but remains legally relevant.")

    # similarity
    explanation_lines.append(
        f"- It is closely related to the input scenario (semantic similarity {sim:.3f})."
    )

    # keyword boost
    if topic > 0:
        explanation_lines.append(
            f"- It discusses trademark-related matters, aligning with the query topic."
        )

    explanation_lines.append(
        "- After filtering procedural cases and re-ranking, this case had the highest overall score."
    )

    return {
        "precedent_case": best,
        "explanation": "\n".join(explanation_lines)
    }


# ---------------------------------------------
# TEST
# ---------------------------------------------
if __name__ == "__main__":
    print("\nRunning final PCR (single precedent mode)...\n")

    query = """
    recommend_precedents(
    criminal assault case where the defendant claims self-defense. 
    the plaintiff argues the force used was excessive and unjustified. 
    "the case raises issues about proportionality and reasonable apprehension of harm.
    
)
    """

    out = find_best_precedent(query)

    print("\n===== FINAL PRECEDENT =====\n")
    print(out["precedent_case"])

    print("\n===== EXPLANATION =====\n")
    print(out["explanation"])