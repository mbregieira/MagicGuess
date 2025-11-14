# combinators.py

from .utils import validate_email
from .generators import (
    generate_from_name, generate_from_email, generate_from_person,
    generate_from_word, expand_leet, generate_pins_from_text
)
from .transforms import date_to_variations


# -------------------------------------
# WORDLIST GENERATOR (MAIN)
# -------------------------------------

def generate_wordlist(mg):

    words = []

    # Name
    words.extend(generate_from_name(mg.name))

    # Emails
    for email in mg.emails:
        if validate_email(email):
            words.extend(generate_from_email(email))

    # Relationships / children / pets
    for rel in mg.relationships:
        words.extend(generate_from_person(rel))

    for child in mg.children:
        words.extend(generate_from_person(child))

    for pet in mg.pets:
        words.extend(generate_from_person(pet))

    # Important dates
    for d in mg.important_dates:
        words.extend(date_to_variations(d))

    # Important words
    for w in mg.keywords:
        words.extend(generate_from_word(w))

    # Expand with leet
    expanded = expand_leet(words, max_subs=2)

    return sorted(set(expanded))


# -------------------------------------
# PINLIST GENERATOR (MAIN)
# -------------------------------------

def generate_pinlist(mg):

    pins = set()

    all_textual_words = []

    # Collect everything that is text-based
    all_textual_words.extend(generate_from_name(mg.name))

    for email in mg.emails:
        if validate_email(email):
            all_textual_words.extend(generate_from_email(email))

    for rel in mg.relationships:
        all_textual_words.extend(generate_from_person(rel))

    for child in mg.children:
        all_textual_words.extend(generate_from_person(child))

    for pet in mg.pets:
        all_textual_words.extend(generate_from_person(pet))

    for w in mg.keywords:
        all_textual_words.extend(generate_from_word(w))

    # Generate PINs from text (T9, digits)
    pins.update(generate_pins_from_text(all_textual_words))

    # Add date-only combos
    for d in mg.important_dates:
        pins.update(date_to_variations(d))

    return sorted(pins)
