from app.rag.retriever import retrieve_relevant_chunks, MAX_RELEVANT_SCORE

QUESTIONS = [
    "Ekipman envanteri ekranı ne işe yarar?",
    "İş Emri Sorumlusu olarak nasıl iş emri oluştururum?",
]

def main():
    print(f"MAX_RELEVANT_SCORE = {MAX_RELEVANT_SCORE}")
    for question in QUESTIONS:
        print("=" * 80)
        print(f"SORU: {question}")
        print("-" * 80)

        chunks = retrieve_relevant_chunks(question, k=5)
        for i, chunk in enumerate(chunks, start=1):
            meta = chunk["metadata"]
            label = f"{meta.get('title', meta.get('source'))}, s. {meta.get('page')}"
            print(f"{i}. score={chunk['score']:.4f}  rerank_score={chunk['rerank_score']:.4f}  [{label}]")
            print(f"   {chunk['content'][:120].replace(chr(10), ' ')}...")
        print()

if __name__ == "__main__":
    main()
