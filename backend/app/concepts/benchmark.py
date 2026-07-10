import json
from pathlib import Path
from app.concepts.resolver import ConceptResolver

BASE_DIR = Path(__file__).resolve().parents[2]
TEST_QUESTIONS_PATH = BASE_DIR / "data" / "concept_test_questions.json"

def run_benchmark() -> None:
    questions = json.loads(TEST_QUESTIONS_PATH.read_text(encoding="utf-8"))

    resolver = ConceptResolver()

    total = 0
    full_hit = 0
    partial_hit = 0

    for item in questions:
        question = item["question"]
        expected = set(item["expected_concepts"])

        concepts = resolver.resolve(question)
        found = set(c["concept_id"] for c in concepts if c.get("concept_id"))

        is_full = expected.issubset(found)
        is_partial = bool(expected.intersection(found))

        total += 1
        full_hit += int(is_full)
        partial_hit += int(is_partial)

        print("=" * 80)
        print("Soru:", question)
        print("Beklenen:", expected)
        print("Bulunan:", found)
        print("Sonuç:", "FULL" if is_full else "PARTIAL" if is_partial else "FAIL")

    print("=" * 80)
    print(f"Full score: {full_hit}/{total}")
    print(f"Partial score: {partial_hit}/{total}")

if __name__ == "__main__":
    run_benchmark()