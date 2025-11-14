# combinações e cross-product das palavras/patterns

from .transforms import (
    normalize_string, extract_digits, date_to_variations,
    email_to_components, split_alphanumeric, string_to_t9
)

def generate_wordlist(mg):

    words = []

    # ------------------------------
    # Target name + components
    # ------------------------------
    name = normalize_string(mg.name)
    if name:
        words.append(name)
        words.extend(split_alphanumeric(name))

    # ------------------------------
    # Email-derived words
    # ------------------------------
    for email in mg.emails:
        parts = email_to_components(email)
        words.extend(parts)
        for p in parts:
            words.extend(split_alphanumeric(p))

    # ------------------------------
    # Relationships / children / pets
    # ------------------------------
    def add_person_entries(person):
        name = normalize_string(person["name"])
        if name:
            words.append(name)
            words.extend(split_alphanumeric(name))

        if person.get("nickname"):
            nick = normalize_string(person["nickname"])
            words.append(nick)

        if person.get("birth"):
            words.extend(date_to_variations(person["birth"]))

    for rel in mg.relationships:
        add_person_entries(rel)

    for child in mg.children:
        add_person_entries(child)

    for pet in mg.pets:
        add_person_entries(pet)

    # ------------------------------
    # Important dates
    # ------------------------------
    for d in mg.important_dates:
        words.extend(date_to_variations(d))

    # ------------------------------
    # Important words
    # ------------------------------
    for w in mg.keywords:
        w = normalize_string(w)
        words.append(w)
        words.extend(split_alphanumeric(w))

    return list(set(words))  # unique


def generate_pinlist(mg):

    pins = set()

    # Base names T9
    def add_t9_from_name(s: str):
        s = normalize_string(s)
        if s:
            t9 = string_to_t9(s)
            if t9:
                pins.add(t9)

    # Target name
    add_t9_from_name(mg.name)

    # Emails
    for email in mg.emails:
        components = email_to_components(email)
        for c in components:
            add_t9_from_name(c)
            digits = extract_digits(c)
            if digits:
                pins.add(digits)

    # Relationships / children / pets
    def add_person(person):
        add_t9_from_name(person["name"])
        if person.get("nickname"):
            add_t9_from_name(person["nickname"])

        if person.get("birth"):
            for combo in date_to_variations(person["birth"]):
                pins.add(combo)

    for rel in mg.relationships:
        add_person(rel)

    for child in mg.children:
        add_person(child)

    for pet in mg.pets:
        add_person(pet)

    # Important dates
    for d in mg.important_dates:
        for combo in date_to_variations(d):
            pins.add(combo)

    # Important words
    for w in mg.keywords:
        add_t9_from_name(w)

    # Remove duplicates
    return sorted(pins)

def dedupe(mg):
    combined = set()

    for w in mg.wordlist:
        combined.add(w)

    for p in mg.pinlist:
        combined.add(p)

    return sorted(combined)