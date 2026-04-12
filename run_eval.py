"""Run all 20 evaluation questions through the API."""
import requests, json

API = "http://localhost:8000/api/search"
QS = [
    "What is neural attention?",
    "What is the difference between generative and discriminative classifiers?",
    "What is the gradient for logistic regression?",
    "What is an N-gram language model?",
    "What is skip-gram in Word2Vec?",
    "How do RNNs work as language models?",
    "What is a 3D rigid body transformation?",
    "Why is weight initialization important in deep learning?",
    "What is network depth in neural networks?",
    "What is cost-sensitive classification?",
    "What is TF-IDF?",
    "What is backpropagation?",
    "What is the Transformer architecture?",
    "What is Word2Vec?",
    "What is Named Entity Recognition?",
    "What is beam search?",
    "What is dropout regularization?",
    "What is batch normalization?",
    "What is transfer learning?",
    "What is the BLEU score?",
]

total = 0
rows = []
for i, q in enumerate(QS, 1):
    r = requests.post(API, json={"query": q, "top_k": 5, "methods": ["fts","vector","tree","metadata"]}, timeout=60)
    d = r.json()
    srcs = d.get("sources", [])[:3]
    best = srcs[0]["score"] if srcs else 0
    total += best
    top3 = []
    for s in srcs:
        bk = s.get("book_id","").replace("_"," ").title()
        pg = s.get("page_idx", 0)
        sc = s.get("score", 0)
        top3.append(f"{bk} p.{pg} ({sc:.4f})")
    while len(top3) < 3:
        top3.append("-")
    print(f"{i}\t{q}\t{best:.4f}\t{top3[0]}\t{top3[1]}\t{top3[2]}")
    rows.append({"q": q, "score": best, "top3": top3})

avg = total / len(QS)
print(f"\nAVERAGE: {avg:.4f} ({avg*100:.1f}%)")
json.dump({"rows": rows, "avg": avg}, open("guide/eval_results.json","w"), indent=2, ensure_ascii=False)
