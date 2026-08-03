import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ROLES_PATH = DATA_DIR / "roles.json"
ROLE_REQUIREMENTS_PATH = DATA_DIR / "role_requirements.json"

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

def chunks_mention_requirement(chunks: list[dict], requirement: dict) -> bool:
    terms = [term.casefold() for term in requirement.get("trigger_terms", [])]
    if not terms:
        return False

    for chunk in chunks:
        content = chunk["content"].casefold()
        if any(term in content for term in terms):
            return True

    return False

def find_missing_required_role(chunks: list[dict],user_roles: list[str] | None,roles: dict,role_requirements: dict) -> str | None:
    user_roles_normalized = normalize_user_roles(user_roles)

    if not user_roles_normalized:
        return None

    if user_roles_normalized.intersection(full_access_role_names(roles)):
        return None

    for requirement in role_requirements.values():
        if not chunks_mention_requirement(chunks, requirement):
            continue
        required_roles = requirement.get("required_roles") or []
        if not required_roles:
            continue
        if not user_roles_normalized.intersection(required_roles):
            return required_roles[0]

    return None