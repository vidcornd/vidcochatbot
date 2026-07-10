from typing import Any
from app.concepts.matcher import ConceptMatcher
from app.concepts.retriever import ConceptRetriever

class ConceptResolver:
    def __init__(self) -> None:
        self.matcher = ConceptMatcher()
        self.retriever = ConceptRetriever()

    def resolve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        exact_matches = self.matcher.exact_match(query)
        exact_matches = sorted(exact_matches,key=lambda item: len(item.get("matched_term", "")),reverse=True,)

        if len(exact_matches) >= 2:
            return exact_matches

        vector_matches = self.retriever.search(query, top_k=top_k)

        merged: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for concept in exact_matches + vector_matches:
            concept_id = concept.get("concept_id")

            if not concept_id or concept_id in seen_ids:
                continue

            if (concept.get("match_type") == "vector" and exact_matches and self._is_conflicting_with_exact(concept, exact_matches)):
                continue

            enriched_concept = self._enrich_concept(concept)

            merged.append(enriched_concept)
            seen_ids.add(concept_id)

            if len(merged) >= top_k:
                break

        return merged

    def _enrich_concept(self, concept: dict[str, Any]) -> dict[str, Any]:
        concept_id = concept.get("concept_id")

        if not concept_id:
            return concept

        concept_from_json = self.matcher.concepts.get(concept_id)

        if not concept_from_json:
            return concept

        enriched = dict(concept)

        enriched.setdefault("name", concept_from_json.get("name"))
        enriched.setdefault("definition", concept_from_json.get("definition"))
        enriched.setdefault("synonyms", concept_from_json.get("synonyms", []))
        enriched.setdefault("examples", concept_from_json.get("examples", []))
        enriched.setdefault("related", concept_from_json.get("related", []))
        enriched.setdefault("distinguish_from",concept_from_json.get("distinguish_from", {}))

        return enriched

    def build_context(self, concepts: list[dict[str, Any]]) -> str:
        if not concepts:
            return ""

        lines = ["İlgili Vidco 17020 kavramları:"]

        for concept in concepts:
            lines.append(f"- {concept.get('name')}: {concept.get('definition')}")

            if concept.get("synonyms"):
                lines.append(f"  Yakın kullanımlar: {', '.join(concept.get('synonyms'))}")

            if concept.get("distinguish_from"):
                lines.append("  Karıştırılmaması gerekenler:")
                for _, explanation in concept.get("distinguish_from").items():
                    lines.append(f"  - {explanation}")

        return "\n".join(lines)

    def _is_conflicting_with_exact(self,candidate: dict[str, Any],exact_matches: list[dict[str, Any]]) -> bool:
        candidate_id = candidate.get("concept_id")

        if not candidate_id:
            return False

        for exact_concept in exact_matches:
            exact_concept_id = exact_concept.get("concept_id")

            if not exact_concept_id:
                continue

            exact_from_json = self.matcher.concepts.get(exact_concept_id, {})
            distinguish_from = exact_from_json.get("distinguish_from", {})

            if candidate_id in distinguish_from:
                return True

        return False