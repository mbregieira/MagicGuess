# utils.py

import os
import platform
import unicodedata
from datetime import datetime
import re

def clear_screen():
    """
    Clear the console screen.
    """
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")

def dedupe(items):
    """
    Remove duplicates from a list while preserving order.
    Returns a list with duplicates removed.
    """
    seen = set()
    clean = []
    for i in items:
        if i not in seen:
            clean.append(i)
            seen.add(i)
    return clean

# Validate if the guess is minimum length, if not, discard
def validate_min_length(list, min_length):
    """
    Validate minimum length of words in a list.
    Returns a list of words that meet the minimum length.
    """
    valid = []
    for word in list:
        if len(word) >= min_length:
            valid.append(word)

    return valid

# Validate date in DD/MM/YYYY format
def validate_date(date_str):
    """
    Validate date in DD/MM/YYYY format.
    Returns True if valid, False otherwise.
    """
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Remove spaces, accents, and non-alphanumeric characters
def sanitize_word(word):
    """
    Sanitize a word by removing spaces, accents, and non-alphanumeric characters.
    Converts to lowercase.
    """
    if not word:
        return ""

    nfkd = unicodedata.normalize("NFKD", word)
    no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
    clean = "".join([c for c in no_accents if c.isalnum()])

    return clean.lower()

# Validate email as string + @ + string + . + string
def validate_email(email):
    """
    Validate email format: string + @ + string + . + string
    """
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

# New normalization function to remove spaces and special characters
def normalize_string(s: str) -> str:
    """
    Normalize a string by removing spaces and special characters, keeping only alphanumeric characters.
    Converts to lowercase.
    """
    return re.sub(r"[^A-Za-z0-9]", "", s)

def all_upper(word: str) -> bool:
    """
    True if all alphabetic characters are uppercase.
    Ignores numbers and special characters.
    """
    letters = [c for c in word if c.isalpha()]
    if not letters:  # if there are no letters, it is not considered "all upper"
        return False
    return all(c.isupper() for c in letters)
