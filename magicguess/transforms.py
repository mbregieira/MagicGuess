# transformações (nome -> pin, leet, phone keypad, etc.)

import re

# ------------------------------
# BASIC NORMALIZERS
# ------------------------------

def normalize_string(s: str) -> str:
    """Lowercase, remove spaces and special chars except digits."""
    return re.sub(r"[^A-Za-z0-9]", "", s.lower())


def extract_digits(s: str) -> str:
    """Return only digits from a string."""
    return "".join(re.findall(r"\d", s))


# ------------------------------
# DATE HANDLING
# ------------------------------

# Convert date object to common password patterns like DDMMYYYY, YYMMDD, etc.
def date_to_variations(date_obj):
    if not date_obj:
        return []

    day = f"{date_obj.day:02d}"
    month = f"{date_obj.month:02d}"
    year = str(date_obj.year)

    return [
        day + month + year,
        day + month + year[2:],   # 241293
        year,
        year[2:],                 # 93
        day + month,               # 2412
        month + year,              # 121993
        month + year[2:],         # 1293
    ]

# ------------------------------
# EMAIL TRANSFORMS
# ------------------------------

# Get left-side of email
def extract_email_username(email: str) -> str:
    """Get left-side of email."""
    return email.split("@")[0].lower()

# Break email into components like user, digits, alpha parts
def email_to_components(email: str):
    user = extract_email_username(email)
    digits = extract_digits(user)
    alpha = re.sub(r"[^A-Za-z]", "", user)

    return [user, digits, alpha]


# ------------------------------
# NAME / NICKNAME / WORD TRANSFORMS
# ------------------------------

def split_alphanumeric(s: str):
    """
    Split a string like 'joaodascouves456123' into:
    - joaodascouves
    - 456123
    """
    parts = re.findall(r"[A-Za-z]+|\d+", s.lower())
    return parts


# ------------------------------
# T9 (OLD PHONE KEYPAD)
# ------------------------------

T9_MAP = {
    "a": "2", "b": "22", "c": "222",
    "d": "3", "e": "33", "f": "333",
    "g": "4", "h": "44", "i": "444",
    "j": "5", "k": "55", "l": "555",
    "m": "6", "n": "66", "o": "666",
    "p": "7", "q": "77", "r": "777", "s": "7777",
    "t": "8", "u": "88", "v": "888",
    "w": "9", "x": "99", "y": "999", "z": "9999",
}


def string_to_t9(s: str) -> str:
    """Convert name → old Nokia numeric keypad representation."""
    s = s.lower()
    return "".join(T9_MAP.get(ch, "") for ch in s if ch.isalpha())

# e.g. c -> 2 not 222 
def string_to_t9_short(s: str) -> str:
    """Convert name → old Nokia numeric keypad representation (short)."""
    s = s.lower()
    t9_short = ""
    added_digits = set()
    for ch in s:
        if ch.isalpha():
            digit = T9_MAP.get(ch, "")[0]  # Get only the first digit
            if digit not in added_digits:
                t9_short += digit
                added_digits.add(digit)
    return t9_short