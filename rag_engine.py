import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, max_chars=1000, overlap=150):
    text = text.replace("\n", " ")
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start += max_chars - overlap
    return chunks

def build_index(chunks):
    embeddings = model.encode(chunks)
    index = NearestNeighbors(metric="cosine")
    index.fit(embeddings)
    return index, embeddings

def search_similar(query, chunks, embeddings, index, top_k=3):
    q_emb = model.encode([query])
    dists, ids = index.kneighbors(q_emb, n_neighbors=top_k)
    return [(chunks[i], 1 - dists[0][j]) for j, i in enumerate(ids[0])]
