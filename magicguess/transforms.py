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

def date_to_variations(date_obj):
    """
    Given a datetime.date object, return common password patterns.
    Example: 24/12/1993 -> ['24121993', '241293', '1993', '93', '2412']
    """
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
        day + month               # 2412
    ]


# ------------------------------
# EMAIL TRANSFORMS
# ------------------------------

def extract_email_username(email: str) -> str:
    """Get left-side of email."""
    return email.split("@")[0].lower()


def email_to_components(email: str):
    """
    Break email username into:
    - raw user
    - digits from user
    - alphabetic blocks
    """
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
