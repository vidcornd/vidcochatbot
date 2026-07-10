def concept_to_text(concept: dict) -> str:
    parts = [f"Kavram: {concept['name']}",
        f"Tanım: {concept['definition']}"]

    if concept.get("synonyms"):
        parts.append(f"Eş anlamlılar: {', '.join(concept['synonyms'])}")

    if concept.get("examples"):
        parts.append(f"Örnekler: {', '.join(concept['examples'])}")

    if concept.get("related"):
        parts.append(f"İlişkili kavramlar: {', '.join(concept['related'])}")

    if concept.get("distinguish_from"):
        parts.append("Karıştırılmaması gereken kavramlar:")
        for other_concept, explanation in concept["distinguish_from"].items():
            parts.append(f"- {concept['name']} kavramı, {other_concept} kavramı ile karıştırılmamalıdır. {explanation}")

    return "\n".join(parts)