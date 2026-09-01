from app.config import origin_matches_allowed_patterns

PATTERNS = ["https://vidco.com.tr", "*.voc-tester.com"]

def test_exact_match_allowed():
    assert origin_matches_allowed_patterns("https://vidco.com.tr", PATTERNS)

def test_unrelated_origin_rejected():
    assert not origin_matches_allowed_patterns("https://evil.com", PATTERNS)

def test_wildcard_subdomain_allowed():
    assert origin_matches_allowed_patterns("https://chatbot.voc-tester.com", PATTERNS)
    assert origin_matches_allowed_patterns("https://musteri1.voc-tester.com", PATTERNS)

def test_wildcard_apex_allowed():
    assert origin_matches_allowed_patterns("https://voc-tester.com", PATTERNS)

def test_wildcard_nested_subdomain_allowed():
    assert origin_matches_allowed_patterns("https://a.b.voc-tester.com", PATTERNS)

def test_wildcard_does_not_allow_suffix_spoofing():
    assert not origin_matches_allowed_patterns("https://voc-tester.com.evil.com", PATTERNS)

def test_wildcard_does_not_allow_prefix_concatenation():
    assert not origin_matches_allowed_patterns("https://evilvoc-tester.com", PATTERNS)


def test_wildcard_does_not_match_different_domain():
    assert not origin_matches_allowed_patterns("https://voc-tester.org", PATTERNS)


def test_no_patterns_rejects_everything():
    assert not origin_matches_allowed_patterns("https://vidco.com.tr", [])

def test_http_and_https_both_match_wildcard():
    assert origin_matches_allowed_patterns("http://test.voc-tester.com", PATTERNS)
    assert origin_matches_allowed_patterns("https://test.voc-tester.com", PATTERNS)