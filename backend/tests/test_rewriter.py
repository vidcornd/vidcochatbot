from app.rag.rewriter import build_route_label_map,enrich_query_with_page,extract_route,page_hint_label
from app.rag.role_guard import load_roles

ROLES = {
    "is_emri_sorumlusu": {
        "name": "İş Emri Sorumlusu",
        "screens": [
            {
                "route": "iso_17020/workorder/listCreate",
                "label": "MUAYENE/ISO 17020 > İş Emirleri > İş Emri Listesi > İş Emri Oluştur (Sorumlu)",
            },
        ],
    },
    "muayene_personeli": {
        "name": "Muayene Personeli",
        "screens": [
            {
                "route": "iso_17020/inspectionreport/oncoming",
                "label": "MUAYENE/ISO 17020 > Muayene Yönetimi > Yaklaşan Muayeneler",
            },
        ],
    },
}

def test_extract_route_from_r_param():
    url = "https://kurulustest.vidco.com.tr/backend.php?r=iso_17020/workorder/listCreate"
    assert extract_route(url) == "iso_17020/workorder/listCreate"

def test_extract_route_with_trailing_params():
    url = "https://kurulustest.vidco.com.tr/backend.php?r=iso_17020/workorder/listCreate&id=42"
    assert extract_route(url) == "iso_17020/workorder/listCreate"

def test_extract_route_missing_r_param():
    assert extract_route("https://kurulustest.vidco.com.tr/dashboard") is None

def test_extract_route_none_input():
    assert extract_route(None) is None
    assert extract_route("") is None

def test_build_route_label_map_covers_all_screens_across_roles():
    mapping = build_route_label_map(ROLES)
    assert mapping["iso_17020/workorder/listCreate"] == "MUAYENE/ISO 17020 > İş Emirleri > İş Emri Listesi > İş Emri Oluştur (Sorumlu)"
    assert mapping["iso_17020/inspectionreport/oncoming"] == "MUAYENE/ISO 17020 > Muayene Yönetimi > Yaklaşan Muayeneler"

def test_page_hint_label_returns_only_last_breadcrumb_segment():
    url = "https://kurulustest.vidco.com.tr/backend.php?r=iso_17020/workorder/listCreate"
    assert page_hint_label(url, ROLES) == "İş Emri Oluştur (Sorumlu)"

def test_page_hint_label_unknown_route_returns_none():
    url = "https://kurulustest.vidco.com.tr/backend.php?r=iso_17020/does/not/exist"
    assert page_hint_label(url, ROLES) is None

def test_page_hint_label_no_current_page_returns_none():
    assert page_hint_label(None, ROLES) is None

def test_enrich_query_with_page_appends_hint():
    url = "https://kurulustest.vidco.com.tr/backend.php?r=iso_17020/workorder/listCreate"
    result = enrich_query_with_page("Nasıl iş emri oluştururum?", url, ROLES)
    assert result == "Nasıl iş emri oluştururum? (İlgili ekran: İş Emri Oluştur (Sorumlu))"

def test_enrich_query_with_page_unchanged_when_no_match():
    assert enrich_query_with_page("Nasıl iş emri oluştururum?", None, ROLES) == "Nasıl iş emri oluştururum?"
    assert enrich_query_with_page("Nasıl iş emri oluştururum?", "https://x.com/unknown", ROLES) == "Nasıl iş emri oluştururum?"

def test_enrich_query_with_page_uses_real_roles_json_by_default():
    real_roles = load_roles()
    mapping = build_route_label_map(real_roles)
    assert len(mapping) > 0

    sample_route, sample_label = next(iter(mapping.items()))
    url = f"https://kurulustest.vidco.com.tr/backend.php?r={sample_route}"
    screen_name = sample_label.split(">")[-1].strip()

    result = enrich_query_with_page("test sorusu", url, real_roles)
    assert screen_name in result