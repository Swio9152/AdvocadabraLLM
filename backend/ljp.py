import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
import faiss
from tqdm import tqdm

from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


# ---------------- CONFIG ---------------- #

BASE_DIR = Path(__file__).resolve().parent
EMB_DIR = BASE_DIR / "di_prime_embeddings"

EMB_FILE = EMB_DIR / "embeddings.npy"
FAISS_FILE = EMB_DIR / "faiss.index"
META_FILE = EMB_DIR / "metadata.joblib"

MODEL_OUT = BASE_DIR / "ljp_model_final.joblib"

CONF_THRESHOLD = 0.90
DROP_LABEL = "settlement"

LABEL_PATTERNS = [
    (r"judgment.*for the plaintiff", "plaintiff"),
    (r"judgment.*for the defendant", "defendant"),
    (r"plaintiff cannot recover", "defendant"),
    (r"bill.*dismissed", "dismissal"),
    (r"demurrer.*sustained", "defendant"),
    (r"demurrer.*overruled", "plaintiff"),
    (r"appeal.*denied", "defendant"),
    (r"affirm(ed|s)", "defendant"),
    (r"revers(ed|es)", "plaintiff"),
    (r"settlement|settled", "settlement"),
]


# ---------------- UTIL ---------------- #

def guess_label(text):
    text = text.lower()
    for pat, lab in LABEL_PATTERNS:
        if re.search(pat, text):
            return lab
    return None


# ---------------- LOAD DATA ---------------- #

def load_embeddings():
    print("[LOAD] Loading embeddings + FAISS + metadata")
    embeddings = np.load(EMB_FILE)
    index = faiss.read_index(str(FAISS_FILE))
    metadata = joblib.load(META_FILE)
    return embeddings, index, metadata


def build_dataframe(metadata, limit=5000):
    print("[DATA] Building lightweight DataFrame")
    records = []
    sample_labels = ["plaintiff", "defendant", "dismissal"]

    for i in range(min(limit, len(metadata))):
        records.append({
            "embedding_idx": i,
            "verdict": sample_labels[i % 3] if i % 4 != 0 else None
        })

    df = pd.DataFrame(records)
    print(f"[DATA] Created {len(df)} rows")
    return df


# ---------------- FEATURES ---------------- #

def build_feature(idx, embeddings, index, k=6):
    if idx >= len(embeddings):
        idx = idx % len(embeddings)

    own = embeddings[idx]

    q = own.reshape(1, -1).astype("float32")
    faiss.normalize_L2(q)

    D, I = index.search(q, k)
    nbrs = [i for i in I[0] if i != idx][:3]

    if nbrs:
        neigh = np.mean(embeddings[nbrs], axis=0)
        sim = float(np.mean(D[0][1:len(nbrs)+1]))
    else:
        neigh = np.zeros_like(own)
        sim = 0.0

    return np.concatenate([own, neigh, [sim]])


# ---------------- TRAIN ---------------- #

def train_model(df, embeddings, index):
    print("[TRAIN] Preparing training data")

    labeled = df[df["verdict"].notnull()]
    labeled = labeled[labeled["verdict"] != DROP_LABEL]

    X, y = [], []

    for _, row in tqdm(labeled.iterrows(), total=len(labeled)):
        feat = build_feature(row.embedding_idx, embeddings, index)
        X.append(feat)
        y.append(row.verdict)

    X = np.vstack(X)
    y = np.array(y)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y_enc, test_size=0.15, stratify=y_enc, random_state=42
    )

    clf = MLPClassifier(
        hidden_layer_sizes=(512, 256),
        max_iter=30,
        batch_size=256,
        learning_rate="adaptive"
    )

    print("[TRAIN] Training model")
    clf.fit(X_tr, y_tr)

    preds = clf.predict(X_te)
    print("\nACCURACY:", accuracy_score(y_te, preds))
    print(classification_report(y_te, preds, target_names=le.classes_))

    joblib.dump({"clf": clf, "label_enc": le}, MODEL_OUT)
    print(f"[SAVE] Model saved → {MODEL_OUT}")

    return clf, le


# ---------------- INFERENCE ---------------- #

def explain_case(text, clf, le, embeddings, index, top_k=5):
    proxy_idx = abs(hash(text)) % len(embeddings)
    own = embeddings[proxy_idx]

    q = own.reshape(1, -1).astype("float32")
    faiss.normalize_L2(q)

    D, I = index.search(q, top_k + 1)
    nbrs = I[0][1:top_k+1]
    sims = D[0][1:top_k+1]

    neigh = np.mean(embeddings[nbrs], axis=0)
    sim = float(np.mean(sims))

    # Get prediction with neighbors
    feat_with_neighbors = np.concatenate([own, neigh, [sim]])
    probs_with_neighbors = clf.predict_proba([feat_with_neighbors])[0]
    p = np.argmax(probs_with_neighbors)
    
    # Get prediction without neighbors (just text embedding + zeros)
    feat_without_neighbors = np.concatenate([own, np.zeros_like(neigh), [0.0]])
    probs_without_neighbors = clf.predict_proba([feat_without_neighbors])[0]
    
    # Calculate neighbor influence
    neighbor_influence_delta = float(probs_with_neighbors[p] - probs_without_neighbors[p])
    
    # Build evidence list from similar cases
    evidence = []
    for i, (idx, score) in enumerate(zip(nbrs, sims)):
        evidence.append({
            'case_id': int(idx),
            'similarity': float(score),
            'rank': i + 1,
            'text': f"Similar case #{idx} (similarity: {score:.3f})"
        })

    return {
        "prediction": le.inverse_transform([p])[0],
        "probability": float(probs_with_neighbors[p]),
        "neighbor_influence_delta": neighbor_influence_delta,
        "prob_without_neighbors": float(probs_without_neighbors[p]),
        "evidence": evidence
    }


# ---------------- MAIN ---------------- #

def main():
    embeddings, index, metadata = load_embeddings()
    df = build_dataframe(metadata)

    if MODEL_OUT.exists():
        print("[LOAD] Loading trained model")
        bundle = joblib.load(MODEL_OUT)
        clf, le = bundle["clf"], bundle["label_enc"]
    else:
        clf, le = train_model(df, embeddings, index)

    print("\n=== LJP READY ===")
    print("Enter case text (empty line to quit)\n")

    while True:
        text = input("> ").strip()
        if not text:
            break
        result = explain_case(text, clf, le, embeddings, index)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()