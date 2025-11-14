# generators.py
#
# Modular generators for each type of information.
# These functions do NOT combine results — they only return lists.
#

from .transforms import (
    normalize_string, split_alphanumeric, extract_digits,
    date_to_variations, email_to_components, string_to_t9,
    leet_transform
)


# ------------------------------
# NAME GENERATOR
# ------------------------------

def generate_from_name(name: str):
    """
    Return base words derived from a name.
    """
    results = []
    if not name:
        return results

    clean = normalize_string(name)
    if clean:
        results.append(clean)
        results.extend(split_alphanumeric(clean))

    return results


# ------------------------------
# EMAIL GENERATOR
# ------------------------------

def generate_from_email(email: str):
    """
    Extract:
    - full username
    - digits
    - alphabetic block
    - alphanumeric splits
    """
    results = []
    parts = email_to_components(email)

    results.extend(parts)

    for p in parts:
        results.extend(split_alphanumeric(p))

    return results


# ------------------------------
# PERSON GENERATOR
# ------------------------------

def generate_from_person(person):
    results = []

    results.extend(generate_from_name(person["name"]))

    if person.get("nickname"):
        results.extend(generate_from_name(person["nickname"]))

    if person.get("birth"):
        results.extend(date_to_variations(person["birth"]))

    return results


# ------------------------------
# IMPORTANT WORD GENERATOR
# ------------------------------

def generate_from_word(word):
    clean = normalize_string(word)
    results = [clean]
    results.extend(split_alphanumeric(clean))
    return results


# ------------------------------
# LEET EXPANSION
# ------------------------------

def expand_leet(words, max_subs=2):
    """
    Apply leet transformation safely, limited by max_subs.
    """
    output = set()

    for w in words:
        if len(w) < 4:
            output.add(w)
            continue

        output.update(leet_transform(w, max_substitutions=max_subs))

    return sorted(output)


# ------------------------------
# PIN GENERATION (T9 + dates + digits)
# ------------------------------

def generate_pins_from_text(words):
    pins = set()

    for w in words:
        t9 = string_to_t9(w)
        if t9:
            pins.add(t9)

        digits = extract_digits(w)
        if digits:
            pins.add(digits)

    return pins

def dedupe(mg):
    combined = set()

    if mg.wordlist:
        combined.update(mg.wordlist)

    if mg.pinlist:
        combined.update(mg.pinlist)

    return sorted(combined)