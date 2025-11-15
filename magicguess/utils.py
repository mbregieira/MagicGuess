# dedupe, shuffle, load/save wordlists

import os
import platform
import unicodedata
from datetime import datetime

def clear_screen():
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")

def dedupe(items):
    """Remove duplicates preserving order."""
    seen = set()
    clean = []
    for i in items:
        if i not in seen:
            clean.append(i)
            seen.add(i)
    return clean

# Validate if the guess is minimum length, if not, discard
def validate_min_length(list, min_length):
    valid = []
    for word in list:
        if len(word) >= min_length:
            valid.append(word)

    return valid

# Validate date in DD/MM/YYYY format
def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Remove spaces, accents, and non-alphanumeric characters
def sanitize_word(word):
    if not word:
        return ""

    nfkd = unicodedata.normalize("NFKD", word)
    no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    clean = "".join([c for c in no_accents if c.isalnum()])

    return clean.lower()

# Validate email as string + @ + string + . + string
def validate_email(email):
    # 1. Check if the email contains exactly one '@' symbol
    if email.count('@') != 1:
        return False

    # Find the position of '@' and the last '.'
    at_index = email.find('@')
    dot_index = email.rfind('.') # Use rfind to find the last occurrence

    # 2. Check for the structure: string + @ + string + . + string
    
    # The '@' must not be the first or the last character
    if at_index == 0 or at_index == len(email) - 1:
        return False

    # The '.' must appear after the '@'
    if dot_index < at_index:
        return False
        
    # The '.' must not be the character immediately following '@'
    if dot_index == at_index + 1:
        return False

    # The '.' must not be the last character
    if dot_index == len(email) - 1:
        return False
        
    # Check that there is at least one character before the '.', e.g., 'a@b.c'
    if dot_index - at_index < 2: 
        return False

    # 3. If all simple checks pass, it adheres to the basic structure.
    return True 
