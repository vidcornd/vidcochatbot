from pathlib import Path

from app.rag.document_id import normalize_document_id
from app.rag.retriever import detect_metadata_filter


def test_android_question_filters_to_android_document():
    assert detect_metadata_filter("Android'de mobil uygulama nasıl kurulur?") == {"doc_id": "mobil-android"}


def test_apple_question_filters_to_apple_document():
    assert detect_metadata_filter("iPhone'a uygulamayı nasıl yüklerim?") == {"doc_id": "mobil-apple"}


def test_ios_and_ipad_also_match_apple():
    assert detect_metadata_filter("iOS kurulumu")["doc_id"] == "mobil-apple"
    assert detect_metadata_filter("iPad kurulumu")["doc_id"] == "mobil-apple"


def test_question_mentioning_both_platforms_is_not_filtered():
    assert detect_metadata_filter("Android ve iOS kurulumu arasındaki fark nedir?") is None


def test_unrelated_question_is_not_filtered():
    assert detect_metadata_filter("Muayene raporu nasıl hazırlanır?") is None


def test_filter_values_match_the_ids_ingest_actually_writes():
    assert detect_metadata_filter("android")["doc_id"] == normalize_document_id(Path("mobil_android.pdf"))
    assert detect_metadata_filter("iphone")["doc_id"] == normalize_document_id(Path("mobil_apple.pdf"))
