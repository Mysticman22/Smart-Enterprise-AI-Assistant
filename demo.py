from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline

app = Flask(__name__)
CORS(app)  # allow React to talk to Flask

# 1. Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Example documents (later: upload + store in DB)
documents = [
    {"text": "Employees are entitled to 20 days of annual leave.", "role": "HR"},
    {"text": "The finance team handles company budgets and invoices.", "role": "Finance"},
]

# 3. Build FAISS index
embeddings = [embedder.encode(doc["text"]) for doc in documents]
dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# 4. Load small local LLM (distilbert as demo → later replace with LLaMA/GPT4All)
qa_model = pipeline("text-generation", model="distilgpt2")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("query", "")
    role = data.get("role", "HR")  # for RBAC (later: from login)

    # Embed query & search docs
    query_vec = embedder.encode([query])
    scores, idx = index.search(np.array(query_vec), k=1)
    best_doc = documents[idx[0][0]]

    # Check role-based restriction
    if best_doc["role"] != role:
        return jsonify({"answer": "Access denied for your role.", "citation": None})

    # Generate answer with context
    context = best_doc["text"]
    prompt = f"Answer based on document: {context}\nQuestion: {query}\nAnswer:"
    answer = qa_model(prompt, max_length=100, do_sample=True)[0]['generated_text']

    return jsonify({
        "answer": answer,
        "citation": context
    })

if __name__ == "__main__":
    import numpy as np
    app.run(host="0.0.0.0", port=5000, debug=True)
