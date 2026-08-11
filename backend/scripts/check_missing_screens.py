from app.rag.generator import answer_question

TEST_CASES = [
    ("Müşteriler ekranında toplu firma kaydı nasıl oluşturulur?", []),
    ("Müşteriler ekranında toplu firma kaydı nasıl oluşturulur?", ["Muayene Personeli"]),
    ("Müşteriler ekranında toplu firma kaydı nasıl oluşturulur?", ["Muayene|ISO 17020 Tanımlama"]),

    ("Ekipman envanteri ekranı ne işe yarar?", ["Muayene Personeli"]),
    ("Ekipman envanteri ekranı ne işe yarar?", ["Muayene|ISO 17020 Tanımlama"]),

    ("Firmaları Excel'e nasıl aktarırım?", ["Muayene Personeli"]),
    ("Firmaları Excel'e nasıl aktarırım?", ["Muayene|ISO 17020 Veri Analizi"]),

    ("Tüm iş emirlerini Excel'e nasıl aktarırım?", ["Muayene Personeli"]),
    ("Tüm iş emirlerini Excel'e nasıl aktarırım?", ["Muayene|ISO 17020 Veri Analizi"]),

    ("İş Emri Uygulama Raporu neyi gösterir?", ["Muayene Personeli"]),
    ("İş Emri Uygulama Raporu neyi gösterir?", ["Muayene|ISO 17020 Veri Analizi"]),

    ("İSG Katip Sözleşmeleri ekranını kimler görebilir?", ["Muayene Personeli"]),
    ("İSG Katip Sözleşmeleri ekranını kimler görebilir?", ["ISG Katip Yöneticisi"]),
    ("İSG Katip Sözleşmeleri ekranını kimler görebilir?", ["Muayene Yöneticisi"]),

    ("İş Emri Sorumlusu olarak nasıl iş emri oluştururum?", ["Muayene Personeli"]),
    ("İş Emri Sorumlusu olarak nasıl iş emri oluştururum?", ["İş Emri Sorumlusu"]),

    ("Toplu iş emri nasıl oluşturulur?", ["İş Emri Yöneticisi"]),
    ("Toplu iş emri nasıl oluşturulur?", ["İş Emri Sorumlusu"]),
    ("Toplu iş emri nasıl oluşturulur?", ["İş Emri Yöneticisi", "İş Emri Sorumlusu"]),
    ("Toplu iş emri nasıl oluşturulur?", ["Admin"]),
]


def main():
    for question, user_roles in TEST_CASES:
        print("=" * 80)
        print(f"SORU: {question}")
        print(f"ROLLER: {user_roles or '(rol bilgisi yok)'}")
        print("-" * 80)

        result = answer_question(question, user_roles=user_roles)

        print("CEVAP:")
        print(result["answer"])

        print("\nKAYNAKLAR:")
        for source in result["sources"]:
            print(f"- {source['title']}, s. {source['page']}")

        print("\nCONFIDENCE:", result["confidence"])
        print()


if __name__ == "__main__":
    main()