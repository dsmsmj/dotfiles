#!/usr/bin/env python3
"""查询产品文档向量库"""
import sys
import json
import chromadb
from sentence_transformers import SentenceTransformer

def main():
    if len(sys.argv) < 2:
        print("用法: python3 query.py \"你的问题\" [返回数量，默认3]")
        sys.exit(1)

    question = sys.argv[1]
    n_results = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    try:
        client = chromadb.HttpClient(host="localhost", port=8000)
        client.heartbeat()
    except Exception:
        # server没起来，降级用本地文件模式
        client = chromadb.PersistentClient(path="/home/muji/my_db")

    collection = client.get_collection("product_docs")

    query_vec = model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=query_vec,
        n_results=n_results
    )

    output = []
    for doc, dist, meta in zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0] if results["metadatas"][0] else [{}] * len(results["documents"][0])
    ):
        output.append({
            "content": doc,
            "relevance_distance": round(dist, 4),
            "metadata": meta
        })

    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
