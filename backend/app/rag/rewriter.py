from urllib.parse import parse_qs, urlparse
from app.rag.chat_models import get_chat_model
from app.rag.role_guard import load_roles

FOLLOW_UP_MARKERS = [
    "peki",
    "sonra",
    "bunu",
    "bunun",
    "bu işlem",
    "bu adım",
    "orada",
    "burada",
    "aynı şekilde",
    "devamında",
    "ne yapacağım",
    "gerekiyor muydu",
    "nasıl olacak",
]

DOMAIN_KEYWORDS = [
    "rapor",
    "muayene",
    "e-imza",
    "imza",
    "android",
    "apple",
    "ios",
    "mobil",
    "şablon",
    "hizmet",
    "firma",
    "müşteri",
    "ölçüm",
    "cihaz",
    "ekipman",
    "iş hijyeni",
    "konfigürasyon",
    "kullanıcı",
    "ayar",
    "tanım",
    "kontrol formu",
    "muayene kontrol formu",
    "rapor formatı",
    "muayene rapor formatı",
    "iş emri",
    "periyodik kontrol",
]

def is_follow_up_question(question: str, memory_context: str = "") -> bool:
    question_lower = question.casefold().strip()

    if not memory_context:
        return False
    
    has_follow_up_marker = False
    has_domain_keyword = False

    for marker in FOLLOW_UP_MARKERS:
        if marker in question_lower:
            has_follow_up_marker = True
            break
            
    for keyword in DOMAIN_KEYWORDS:
        if keyword in question_lower:
            has_domain_keyword = True
            break

    is_short = len(question_lower.split()) <= 4

    if has_follow_up_marker and not has_domain_keyword:
        return True

    if is_short and has_follow_up_marker:
        return True

    return False


def rewrite_follow_up_question(question: str,memory_context: str = "",concept_context: str = "") -> str:
    should_rewrite = is_follow_up_question(question=question,memory_context=memory_context)

    if not should_rewrite and not concept_context:
        return question

    prompt = f"""
Aşağıdaki bilgileri kullanarak kullanıcının son sorusunu bağımsız ve açık bir RAG arama sorgusuna dönüştür.

Amaç:
- "bunu", "sonra", "orada", "peki" gibi belirsiz ifadeleri önceki konuşma bağlamına göre netleştir.
- Vidco 17020 kullanım kılavuzlarında aranabilir, kısa ve açık bir sorgu üret.
- Cevap verme, sadece yeniden yazılmış arama sorgusunu döndür.
- Türkçe yaz.
- Kullanıcının asıl niyetini koru.
- Kavramları karıştırma.

Özellikle şu ayrımlara dikkat et:
- Ekipman: kontrol edilen varlık.
- Cihaz: ölçüm veya test yapmak için kullanılan araç.
- Muayene raporu: gerçek resmi çıktı dokümanı.
- Muayene rapor formatı: rapor şablonu.
- Muayene kontrol formu: sahada veri girişi/kontrol soruları için kullanılan form.

Konuşma geçmişi:
{memory_context if memory_context else "Yok."}

İlgili Vidco 17020 kavram bağlamı:
{concept_context if concept_context else "Yok."}

Son kullanıcı sorusu:
{question}

Yeniden yazılmış bağımsız RAG arama sorgusu:
""".strip()

    try:
        llm = get_chat_model()
        response = llm.invoke(prompt)
        rewritten_query = response.content.strip()

        if not rewritten_query:
            return question

        return rewritten_query

    except Exception:
        return question

def extract_route(current_page: str | None) -> str | None:
    if not current_page:
        return None

    query_params = parse_qs(urlparse(current_page).query)
    route = query_params.get("r", [None])[0]
    return route or None

def build_route_label_map(roles: dict) -> dict[str, str]:
    mapping = {}
    for data in roles.values():
        for screen in data.get("screens", []):
            mapping[screen["route"]] = screen["label"]
    return mapping

def page_hint_label(current_page: str | None, roles: dict) -> str | None:
    route = extract_route(current_page)
    if not route:
        return None

    label = build_route_label_map(roles).get(route)
    if not label:
        return None
    
    return label.split(">")[-1].strip()

def enrich_query_with_page(query: str, current_page: str | None, roles: dict | None = None) -> str:
    roles = load_roles() if roles is None else roles
    screen_name = page_hint_label(current_page, roles)

    if not screen_name:
        return query

    return f"{query} (İlgili ekran: {screen_name})"