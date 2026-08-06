import json
from pathlib import Path
import pytest
from app.rag.role_guard import find_missing_required_role, load_roles, load_role_requirements

FIXTURES_PATH = Path(__file__).resolve().parents[1] / "data" / "role_requirements_fixtures.json"

def load_fixtures() -> list[tuple[str, str, str]]:
    if not FIXTURES_PATH.exists():
        return []

    fixtures = json.load(open(FIXTURES_PATH, encoding="utf-8"))
    return [(key, data["chunk_text"], data["required_role"]) for key, data in fixtures.items()]

def make_chunk(content: str) -> dict:
    return {"content": content}

@pytest.mark.parametrize("requirement_key,chunk_text,required_role", load_fixtures())
def test_generated_requirement_blocks_unauthorized_user(requirement_key, chunk_text, required_role):
    roles = load_roles()
    role_requirements = load_role_requirements()
    assert requirement_key in role_requirements

    result = find_missing_required_role([make_chunk(chunk_text)], ["Muayene Personeli"], roles, role_requirements)
    if required_role == "Muayene Personeli":
        pytest.skip("required_role zaten Muayene Personeli, bu senaryo mismatch testi için uygun değil")
    assert result == required_role

@pytest.mark.parametrize("requirement_key,chunk_text,required_role", load_fixtures())
def test_generated_requirement_passes_for_authorized_user(requirement_key, chunk_text, required_role):
    roles = load_roles()
    role_requirements = load_role_requirements()

    result = find_missing_required_role([make_chunk(chunk_text)], [required_role], roles, role_requirements)
    assert result is None