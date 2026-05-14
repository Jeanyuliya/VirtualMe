import re

PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"(?:\+?886[- ]?)?0?9\d{2}[- ]?\d{3}[- ]?\d{3}\b"),
    "taiwan_id": re.compile(r"\b[A-Z][12]\d{8}\b"),
    "name_like_pattern": re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"),
}


def detect_pii(text: str) -> list[str]:
    return [label for label, pattern in PATTERNS.items() if pattern.search(text)]
