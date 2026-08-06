"""
Kullanım:
    python -m scripts.expand_role_requirements
    python -m scripts.expand_role_requirements --dry-run
    python -m scripts.expand_role_requirements --limit 5
"""
import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path
import fitz
from app.logging_config import configure_logging
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_DIR = DATA_DIR / "raw"
ROLES_PATH = DATA_DIR / "roles.json"
ROLE_REQUIREMENTS_PATH = DATA_DIR / "role_requirements.json"
FIXTURES_PATH = DATA_DIR / "role_requirements_fixtures.json"
REPORT_PATH = Path(__file__).resolve().parent / "expand_role_requirements_report.txt"

EXCLUDED_ROLE_IDS = {"sistem_yoneticisi"}
MIN_PASSAGE_LENGTH = 60
PASSAGE_WINDOW = 500

def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

def build_candidates(roles: dict, role_requirements: dict) -> list[dict]:
    covered_routes = {req["route"] for req in role_requirements.values() if "route" in req}

    route_to_roles = defaultdict(list)
    route_to_label = {}
    for role_id, data in roles.items():
        if data.get("full_access") or role_id in EXCLUDED_ROLE_IDS:
            continue
        for screen in data.get("screens", []):
            route_to_roles[screen["route"]].append(data["name"])
            route_to_label[screen["route"]] = screen["label"]

    candidates = []
    for route, required_roles in sorted(route_to_roles.items()):
        if route in covered_routes:
            continue
        label = route_to_label[route]
        screen_name = label.split(">")[-1].strip()
        candidates.append({"route": route, "label": label, "screen_name": screen_name, "required_roles": required_roles})

    return candidates

def load_raw_texts() -> dict[str, str]:
    texts = {}
    for path in sorted(RAW_DIR.glob("*.pdf")):
        doc = fitz.open(path)
        texts[path.name] = "\n".join(page.get_text("text") for page in doc)
        doc.close()
    return texts

def find_passages(screen_name: str, raw_texts: dict[str, str]) -> list[dict]:
    if not screen_name or len(screen_name) < 4:
        return []

    half_window = PASSAGE_WINDOW // 2

    passages = []
    for filename, text in raw_texts.items():
        for block in text.split("\n\n"):
            block = block.strip()
            if len(block) < MIN_PASSAGE_LENGTH:
                continue
            match_at = block.find(screen_name)
            if match_at == -1:
                continue

            window_start = max(0, match_at - half_window)
            window_end = min(len(block), match_at + len(screen_name) + half_window)
            window_text = block[window_start:window_end]
            if screen_name not in window_text:
                continue  

            passages.append({"source": filename, "text": window_text})
    return passages

def passage_mentions_conflicting_roles(passage_text: str, required_roles: list[str], all_role_names: list[str]) -> list[str]:
    passage_cf = passage_text.casefold()
    mentioned = {name for name in all_role_names if name.casefold() in passage_cf}
    return sorted(mentioned - set(required_roles))

def propose_trigger_terms(llm, label: str, required_roles: list[str], passage_text: str) -> list[str]:
    prompt = f"""Aşağıda Vidco 17020 sisteminin bir ekranını anlatan GERÇEK bir doküman pasajı var.

Ekran: {label}
Bu ekranı görebilen rol(ler): {", ".join(required_roles)}

Pasaj:
\"\"\"
{passage_text}
\"\"\"

Görevin: bu pasajdan, SADECE bu ekranı/işlemi ayırt eden, 1-3 tane KISA (5-15 kelime)
ifade seç. Kurallar:
- İfadeler pasajdan BİREBİR alıntı olmalı -- pasajın içinden doğrudan COPY-PASTE et,
  tek bir harf/noktalama/boşluk bile değiştirme, eş anlamlısını yazma, özetleme.
  Yazdığın ifadeyi pasajın içinde Ctrl+F ile arasak bulunmalı.
- Genel/başka bağlamlarda da geçebilecek kısa ifadeler seçme (örn. "Yeni Ekle").
- Pasaj bu ekranla ilgili değilse veya rol kısıtlaması içermiyorsa boş liste döndür.

Yalnızca şu JSON formatında cevap ver, başka hiçbir şey yazma, açıklama ekleme:
{{"trigger_terms": ["...", "..."]}}"""

    response = llm.invoke(prompt)
    content = response.content.strip()
    if content.startswith("```"):
        content = content.strip("`").removeprefix("json").strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            logger.warning("LLM yanıtı JSON olarak parse edilemedi: %r", content[:200])
            return []
        try:
            parsed = json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            logger.warning("LLM yanıtı JSON olarak parse edilemedi: %r", content[:200])
            return []

    return parsed.get("trigger_terms") or []

def verify_term(term: str, passage_text: str, raw_texts: dict[str, str]) -> bool:
    if term not in passage_text:
        return False
    hits = [f for f, text in raw_texts.items() if term in text]
    return len(hits) == 1

def key_from_route(route: str) -> str:
    tail = route.removeprefix("iso_17020/")
    return "".join(ch if ch.isalnum() else "_" for ch in tail.lower()).strip("_")

def main():
    configure_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="LLM çağırma, sadece adayları ve pasaj eşleşmelerini bas")
    parser.add_argument("--limit", type=int, default=None, help="En fazla bu kadar aday işle")
    args = parser.parse_args()

    roles = load_json(ROLES_PATH)
    role_requirements = load_json(ROLE_REQUIREMENTS_PATH)
    fixtures = load_json(FIXTURES_PATH) if FIXTURES_PATH.exists() else {}
    all_role_names = [data["name"] for data in roles.values() if not data.get("full_access")]

    candidates = build_candidates(roles, role_requirements)
    if args.limit:
        candidates = candidates[: args.limit]
    logger.info("Toplam %d aday ekran (zaten kapsananlar hariç)", len(candidates))

    raw_texts = load_raw_texts()

    llm = None
    if not args.dry_run:
        try:
            from app.rag.chat_models import get_chat_model
            llm = get_chat_model()
        except Exception as error:
            logger.warning("LLM başlatılamadı (%s), --dry-run gibi devam ediliyor", error)

    added = []
    needs_review = []
    no_match = []
    rejected = []  

    for candidate in candidates:
        passages = find_passages(candidate["screen_name"], raw_texts)
        if not passages:
            no_match.append(candidate)
            continue

        if llm is None:
            logger.info("[EŞLEŞME] %s -> %s (%d pasaj, LLM çağrılmadı)", candidate["route"], [p["source"] for p in passages], len(passages))
            continue

        conflicting_passages = [
            (p, passage_mentions_conflicting_roles(p["text"], candidate["required_roles"], all_role_names))
            for p in passages
        ]
        conflicting_passages = [(p, c) for p, c in conflicting_passages if c]
        if conflicting_passages:
            for passage, conflicts in conflicting_passages:
                needs_review.append({**candidate, "source": passage["source"], "reason": f"pasajda geçen ama required_roles'te olmayan roller: {conflicts}", "passage": passage["text"]})
            continue

        candidate_added = False
        candidate_attempts = []  

        for passage in passages:
            proposed_terms = propose_trigger_terms(llm, candidate["label"], candidate["required_roles"], passage["text"])
            verified_terms = [t for t in proposed_terms if verify_term(t, passage["text"], raw_texts)]
            candidate_attempts.append({"source": passage["source"], "proposed": proposed_terms, "verified": verified_terms})

            if not verified_terms:
                continue

            key = key_from_route(candidate["route"])
            assert key not in role_requirements, f"route bazlı anahtar çakıştı: {key} ({candidate['route']})"

            role_requirements[key] = {
                "route": candidate["route"],
                "required_roles": candidate["required_roles"],
                "trigger_terms": verified_terms,
            }
            fixtures[key] = {"chunk_text": passage["text"], "required_role": candidate["required_roles"][0], "source": passage["source"]}
            added.append(key)
            candidate_added = True
            break  

        if not candidate_added and candidate_attempts:
            rejected.append({**candidate, "attempts": candidate_attempts})

    if added:
        save_json(ROLE_REQUIREMENTS_PATH, role_requirements)
        save_json(FIXTURES_PATH, fixtures)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(f"Eklenen ({len(added)}): {added}\n\n")
        f.write(f"İnsan incelemeli / çelişkili ({len(needs_review)}):\n")
        for item in needs_review:
            f.write(f"  - {item['route']} ({item['source']}): {item['reason']}\n")
        f.write(f"\nPasaj bulundu ama LLM'in önerdiği hiçbir terim doğrulanamadı ({len(rejected)}):\n")
        for item in rejected:
            f.write(f"  - {item['route']} ({item['label']})\n")
            for attempt in item["attempts"]:
                f.write(f"      [{attempt['source']}] önerilen={attempt['proposed']!r} doğrulanan={attempt['verified']!r}\n")
        f.write(f"\nEşleşme bulunamayan ({len(no_match)}):\n")
        for item in no_match:
            f.write(f"  - {item['route']} ({item['label']})\n")

    logger.info(
        "Bitti. Eklenen=%d, insan-incelemeli=%d, reddedilen=%d, eşleşmeyen=%d. Rapor: %s",
        len(added), len(needs_review), len(rejected), len(no_match), REPORT_PATH,
    )

if __name__ == "__main__":
    main()