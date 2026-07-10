import json
from pathlib import Path
from typing import Any

GENERIC_EXACT_TERMS = {
    "kontrol",
    "muayene",
    "rapor",
    "hizmet",
    "iş",
    "kayıt",
    "belge",
    "form",
    "format",
    "varlık",
    "alan",
    "tarih",
    "geçerlilik",
}

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CONCEPTS_PATH = BASE_DIR / "data" / "concepts.json"

class ConceptMatcher:
    def __init__(self, concepts_path: str | Path = DEFAULT_CONCEPTS_PATH):
        self.concepts = self._load_concepts(Path(concepts_path))
        self.reserved_terms = self._build_reserved_terms()

    def _load_concepts(self, concepts_path: Path) -> dict[str, dict[str, Any]]:
        if not concepts_path.exists():
            raise FileNotFoundError(f"Concepts file not found: {concepts_path}")

        concepts = json.loads(concepts_path.read_text(encoding="utf-8"))

        if not isinstance(concepts, dict):
            raise ValueError("concepts.json must be a JSON object.")

        return concepts

    def exact_match(self, query: str) -> list[dict[str, Any]]:
        query_lower = query.lower()
        matches: list[dict[str, Any]] = []

        for concept_id, concept in self.concepts.items():
            terms = self._get_match_terms(concept)

            for term in terms:
                if term.lower() in query_lower:
                    matches.append({
                            "concept_id": concept_id,
                            "name": concept["name"],
                            "definition": concept["definition"],
                            "synonyms": concept.get("synonyms", []),
                            "examples": concept.get("examples", []),
                            "related": concept.get("related", []),
                            "distinguish_from": concept.get("distinguish_from", {}),
                            "match_type": "exact",
                            "matched_term": term}
                    )
                    break

        return matches

    def _build_reserved_terms(self) -> set[str]:
        reserved_terms: set[str] = set()

        for concept in self.concepts.values():
            reserved_terms.add(concept["name"].casefold().strip())

            for synonym in concept.get("synonyms", []):
                reserved_terms.add(synonym.casefold().strip())

        return reserved_terms

    def _get_match_terms(self, concept: dict[str, Any]) -> list[str]:
        name_and_synonyms = [concept["name"]] + concept.get("synonyms", [])
        examples = concept.get("examples", [])

        safe_examples = [example
            for example in examples
            if example.casefold().strip() not in self.reserved_terms]

        terms = name_and_synonyms + safe_examples

        return [term
            for term in terms
            if term.casefold().strip() not in GENERIC_EXACT_TERMS]