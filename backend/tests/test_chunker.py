from pathlib import Path
import fitz
from app.rag.chunker import create_chunks

PDF_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "is_emri_ve_muayene_yonetimi.pdf"

def _load_pages(pdf_path: Path) -> list[dict]:
    doc = fitz.open(str(pdf_path))
    pages = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if not text:
            continue

        pages.append({
            "text": text,
            "metadata": {
                "source": pdf_path.name,
                "title": "17020 İş Emri ve Muayene Yönetimi",
                "page": page_number,
            },
        })

    return pages

def test_self_approval_chunk_is_not_mixed_with_unrelated_topics():
    pages = _load_pages(PDF_PATH)
    chunks = create_chunks(pages)

    target = next((c for c in chunks if "kendi muayenesini kendisi onaylayabilir" in c.page_content),None)

    assert target is not None, "Beklenen cümleyi içeren chunk bulunamadı"
    assert "Mobil Üzerinden Muayene ve Düzenleme" not in target.page_content
    assert "Yeni Muayene ve Hazır Rapor Ekleme" not in target.page_content
    assert target.page_content.startswith("Muayeneyi Onaya Gönderme Akışı")