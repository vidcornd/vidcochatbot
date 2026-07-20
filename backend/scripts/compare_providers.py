from app.config import settings
from app.services.rag_service import RagService

TEST_CASES = [
    ("Muayene onay personeli kendi yaptığı muayeneyi onaylayabilir mi?", "chunking + liste biçimi"),
    ("Cihazın periyodik kontrolü ile ekipmanın periyodik kontrolü aynı mı?", "concept guard / resolver regresyonu"),
    ("Bugün dolar kaç TL?", "fallback / router"),
    ("Rapor hazırlama rehberinde geçen ${C_sgkSicilNo} parametresi ne işe yarar?", "parametre formatı"),
    ("SGK sicil numarası firma bilgisinden mi geliyor, yoksa şubeden mi?", "çapraz doküman sentezi"),
    ("Cihaz tanınmıyor", "belirsiz soru, dürüst cevap"),
    ("Muayeneleri onaylayan kişi otomatik olarak nasıl değiştirilir?", "doküman boşluğu, uydurmama"),
    ("Ekipmanın kontrol-geçerlilik-onay tarihi nasıl görüntülenir?", "ekipman/cihaz karışıklığı"),
    ("Muayeneyi onaya göndermeye çalışıyorum ancak isg katip sözleşmemi yüklenmeli hatası alıyorum", "destek notu regresyonu"),
]

def run_for_provider(provider: str) -> None:
    settings.chat_provider = provider
    rag_service = RagService()
    print(f"\n{'=' * 80}\nSAĞLAYICI: {provider}\n{'=' * 80}")

    for question, label in TEST_CASES:
        print(f"\n--- [{label}] {question} ---")

        try:
            result = rag_service.answer(question)
        except Exception as error:
            print(f"HATA: {error}")
            continue

        print(result["answer"])
        print("Kaynaklar:", [source.get("title") for source in result["sources"]])
        print("Confidence:", result["confidence"])

def main():
    original_provider = settings.chat_provider

    try:
        run_for_provider("gemini")
        run_for_provider("deepseek")
    finally:
        settings.chat_provider = original_provider

if __name__ == "__main__":
    main()