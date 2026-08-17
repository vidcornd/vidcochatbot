import json
from pathlib import Path
import re

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ROLES_PATH = DATA_DIR / "roles.json"
ROLE_REQUIREMENTS_PATH = DATA_DIR / "role_requirements.json"

def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text)

def load_roles() -> dict:
    with open(ROLES_PATH, encoding="utf-8") as f:
        return json.load(f)

def load_role_requirements() -> dict:
    with open(ROLE_REQUIREMENTS_PATH, encoding="utf-8") as f:
        return json.load(f)

def normalize_user_roles(user_roles: list[str] | None) -> set[str]:
    return {role.strip() for role in (user_roles or []) if role.strip()}

def full_access_role_names(roles: dict) -> set[str]:
    return {data["name"] for data in roles.values() if data.get("full_access")}

def chunk_mentions_requirement(chunk: dict, requirement: dict) -> bool:
    terms = [_normalize_whitespace(term.casefold()) for term in requirement.get("trigger_terms", [])]
    if not terms:
        return False

    content = _normalize_whitespace(chunk["content"].casefold())
    return any(term in content for term in terms)

def missing_role_for_requirement(requirement: dict, user_roles_normalized: set[str]) -> str | None:
    required_roles_all = requirement.get("required_roles_all")
    if required_roles_all:
        missing = [role for role in required_roles_all if role not in user_roles_normalized]
        return missing[0] if missing else None

    required_roles = requirement.get("required_roles") or []
    if not required_roles:
        return None

    if user_roles_normalized.intersection(required_roles):
        return None

    return required_roles[0]

def most_relevant_chunk(chunks: list[dict]) -> dict:
    return min(chunks, key=lambda chunk: chunk.get("score", float("inf")))

def find_missing_required_role(chunks: list[dict],user_roles: list[str] | None,roles: dict,role_requirements: dict) -> str | None:
    user_roles_normalized = normalize_user_roles(user_roles)

    if not user_roles_normalized:
        return None

    if user_roles_normalized.intersection(full_access_role_names(roles)):
        return None

    if not chunks:
        return None

    primary_chunk = most_relevant_chunk(chunks)

    for requirement in role_requirements.values():
        if not chunk_mentions_requirement(primary_chunk, requirement):
            continue

        missing_role = missing_role_for_requirement(requirement, user_roles_normalized)
        if missing_role:
            return missing_role

    return None