from app.rag.generator import answer_question


TEST_QUESTIONS = [
    "Vidco 17020'de muayene raporu nasıl hazırlanır?",
    "Hazır rapor şablonu nasıl eklenir?",
    "Android mobil uygulama nasıl kurulur?",
    "Apple cihazda mobil uygulama nasıl kurulur?",
    "İş hijyeni süreci nasıl ilerler?",
    "Temel ayarlar nereden yapılır?",
    "Bugün dolar kaç TL?",
]


def main():
    for question in TEST_QUESTIONS:
        print("=" * 80)
        print(f"SORU: {question}")
        print("-" * 80)

        result = answer_question(question)

        print("CEVAP:")
        print(result["answer"])

        print("\nKAYNAKLAR:")
        for source in result["sources"]:
            print(f"- {source['title']}, s. {source['page']}")

        print("\nCONFIDENCE:", result["confidence"])


if __name__ == "__main__":
    main()