from pathlib import Path
import fitz


DOCUMENT_TITLES = {
    "17020_temel_ayarlari.pdf": "17020 Muayene Yazılımı Temel Ayarları",
    "e_imza_sureci_direct.pdf": "E-imza Süreci Direct Kullanım Kılavuzu",
    "firmalar.pdf": "Firmalar",
    "hazir_sablon_ekleme.pdf": "Muayene Raporu Hazır Şablon Ekleme Kılavuzu",
    "is_hijyeni_raporu_template.pdf": "İş Hijyeni Raporu Şablonu",
    "is_hijyeni_surec_yonetimi.pdf": "İş Hijyeni Süreç Yönetimi Kılavuzu",
    "iso_17020_konfigurasyonlari.pdf": "Muayene/ISO 17020 Konfigürasyonları",
    "kullanici_ayar_tanimlari.pdf": "Kullanıcı Ayar ve Tanımları",
    "mobil_android.pdf": "Mobil Uygulama Yükleme Android Kılavuzu",
    "mobil_apple.pdf": "Mobil Uygulama Yükleme Apple Kılavuzu",
    "musteri_yonetimi_temel_ayarlari.pdf": "Müşteri Yönetimi Temel Ayarları",
    "olcum_cihazlari.pdf": "Ölçüm Cihazları",
    "rapor_hazirlama_parametre_rehberi.pdf": "17020 Muayene Raporu Hazırlama ve Parametre Kullanım Rehberi",
}

def load_all_pdfs(raw_dir: str = "data/raw") -> list[dict]:
    raw_path = Path(raw_dir)
    pdf_files = sorted(raw_path.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {raw_dir}")

    all_pages = []
    for pdf_file in pdf_files:
        pages = load_pdf(str(pdf_file))
        all_pages.extend(pages)
        print(f"Loaded {pdf_file.name}: {len(pages)} pages")

    print(f"Total PDF files: {len(pdf_files)}")
    print(f"Total pages loaded: {len(all_pages)}")

    return all_pages

def load_pdf(pdf_path: str) -> list[dict]:
    path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if not text:
            continue

        pages.append({
                "text": text,
                "metadata": {
                    "source": path.name,
                    "title": DOCUMENT_TITLES.get(path.name, path.stem),
                    "page": page_number
                }
            })

    doc.close()
    return pages