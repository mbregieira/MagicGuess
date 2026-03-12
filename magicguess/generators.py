# generators.py

from magicguess.utils import sanitize_word, dedupe, normalize_string, all_upper
from datetime import datetime
from pathlib import Path
import itertools
import re

SPECIAL_CHARS = ['!', '@', '#', '$', '%', '&', '*', '"']
MIN_WORDLIST_LENGTH = 5

# -------------------------
# LEET MAPPING
# -------------------------
LEET_MAP = {
    "a": ["4", "@"],
    "e": ["3"],
    "i": ["1", "!", "|"],
    "o": ["0"],
    "s": ["5"]
}

def apply_leet(word):
    """
    Applies substitutions, only 1 letter at a time to avoid explosion.
    """
    variants = set([word])

    for idx, ch in enumerate(word.lower()):
        if ch in LEET_MAP:
            for sub in LEET_MAP[ch]:
                new_word = list(word)
                new_word[idx] = sub
                variants.add("".join(new_word))

    return list(variants)


# -------------------------
# T9 mapping 
# -------------------------
T9_MAP = {
    'a': '2', 'b': '2', 'c': '2',
    'd': '3', 'e': '3', 'f': '3',
    'g': '4', 'h': '4', 'i': '4',
    'j': '5', 'k': '5', 'l': '5',
    'm': '6', 'n': '6', 'o': '6',
    'p': '7', 'q': '7', 'r': '7', 's': '7',
    't': '8', 'u': '8', 'v': '8',
    'w': '9', 'x': '9', 'y': '9', 'z': '9'
}

# -------------------------
# T9 multi-press mapping (e.g. a=2, b=22, c=222)
# -------------------------
T9_MULTI_MAP = {
    'a': '2', 'b': '22', 'c': '222',
    'd': '3', 'e': '33', 'f': '333',
    'g': '4', 'h': '44', 'i': '444',
    'j': '5', 'k': '55', 'l': '555',
    'm': '6', 'n': '66', 'o': '666',
    'p': '7', 'q': '77', 'r': '777', 's': '7777',
    't': '8', 'u': '88', 'v': '888',
    'w': '9', 'x': '99', 'y': '999', 'z': '9999',
}

def string_to_t9(s: str) -> str:
    """
    Convert letters to old phone keypad digits
    """
    if not s:
        return ""
    s = ''.join(ch for ch in s.lower() if ch.isalpha())
    return ''.join(T9_MAP.get(ch, '') for ch in s)


def string_to_t9_multi(s: str) -> str:
    """
    Convert letters to multi-press keypad representation (repeat digits per letter).
    """
    if not s:
        return ""
    s = ''.join(ch for ch in s.lower() if ch.isalpha())
    return ''.join(T9_MULTI_MAP.get(ch, '') for ch in s)

# -------------------------
# Hyphenated name handling
# -------------------------
def sanitize_name_preserve_hyphen(name: str):
    """
    Sanitize a name while preserving hyphens (for hyphenated names).
    Only removes special characters except hyphens.
    """
    if not name:
        return ""
    # Remove special chars but keep letters, hyphens, and spaces
    cleaned = re.sub(r'[^a-zA-Z\-\s]', '', name)
    return cleaned.strip()

def split_hyphenated_name(name: str):
    """
    Split hyphenated names and return both with and without hyphen.
    
    Examples:
        "Paul-Philipp" -> ["Paul-Philipp", "Paul", "Philipp"]
        "Smith-Johnson" -> ["Smith-Johnson", "Smith", "Johnson"]
        "Normal" -> ["Normal"]
    
    Returns list of sanitized name parts.
    """
    if not name:
        return []
    
    if '-' in name:
        # Keep the hyphenated version
        full_hyphenated = sanitize_name_preserve_hyphen(name)
        # Also get the parts without hyphen
        parts = [sanitize_word(p) for p in name.split('-') if p.strip()]
        
        # Return: hyphenated version + individual parts
        result = [full_hyphenated] + parts
        return [r for r in result if r]
    else:
        # No hyphen - use regular sanitize
        sanitized = sanitize_word(name)
        return [sanitized] if sanitized else []


def parse_name_components(full_name: str):
    """
    Parse a full name into components.
    
    Returns a dict with:
        - 'first_names': list of first name variants (with hyphen + split parts)
        - 'middle_names': list of middle name variants
        - 'last_names': list of last name variants (with hyphen + split parts)
        - 'all_parts': flat list of all individual parts including hyphenated versions
    """
    if not full_name:
        return {'first_names': [], 'middle_names': [], 'last_names': [], 'all_parts': []}
    
    parts_raw = [p for p in full_name.strip().split() if p]
    
    if not parts_raw:
        return {'first_names': [], 'middle_names': [], 'last_names': [], 'all_parts': []}
    
    # Process first name 
    first_variants = split_hyphenated_name(parts_raw[0])
    
    # Process last name
    last_variants = split_hyphenated_name(parts_raw[-1]) if len(parts_raw) > 1 else []
    
    # Process middle names (if any)
    middle_variants = []
    if len(parts_raw) > 2:
        for middle in parts_raw[1:-1]:
            middle_variants.extend(split_hyphenated_name(middle))
    
    # Collect all individual parts
    all_parts = first_variants + middle_variants + last_variants
    
    return {
        'first_names': first_variants,
        'middle_names': middle_variants,
        'last_names': last_variants,
        'all_parts': dedupe(all_parts)
    }


# -------------------------
# Toggle case
# -------------------------
def toggle_case(word):
    """
    Generate case variants.
    """
    if not word:
        return []
    
    return dedupe([
        word.lower(),
        word.capitalize()
    ])

# -------------------------
# Name variants 
# -------------------------
def name_variants(full_name: str):
    """
    Generates name variants for passwords.
    """
    components = parse_name_components(full_name)
    
    if not components['all_parts']:
        return []
    
    variants = []
    
    # 1. INDIVIDUAL PARTS (lowercase and Capitalized)
    for part in components['all_parts']:
        if '-' in part:
            # For hyphenated parts, handle capitalization specially
            hyphen_parts = part.split('-')
            
            # All lowercase
            variants.append(part.lower())
            
            # Each part capitalized: Paul-Philipp
            capitalized_hyphen = '-'.join([p.capitalize() for p in hyphen_parts])
            variants.append(capitalized_hyphen)
            
            # First part capitalized, rest lowercase: Paul-philipp
            if len(hyphen_parts) >= 2:
                first_cap_rest_lower = hyphen_parts[0].capitalize() + '-' + '-'.join([p.lower() for p in hyphen_parts[1:]])
                variants.append(first_cap_rest_lower)
        else:
            # Regular parts without hyphen
            variants.append(part.lower())
            variants.append(part.capitalize())
    
    # 2. FIRST + LAST combinations
    if components['first_names'] and components['last_names']:
        # components['first_names'] = ['Paul-Philipp', 'Paul', 'Philipp'] if hyphenated
        # We want: Paul+Last, PaulPhilipp+Last, AND Paul-Philipp+Last
        
        # Get the hyphenated version if it exists
        first_hyphenated = components['first_names'][0] if '-' in components['first_names'][0] else None
        # Get the first part (Paul)
        first_single = components['first_names'][1] if len(components['first_names']) > 1 else components['first_names'][0]
        # Get combined without hyphen (PaulPhilipp)
        first_combined = components['first_names'][0].replace('-', '') if first_hyphenated else first_single
        
        # Same for last name
        last_hyphenated = components['last_names'][0] if '-' in components['last_names'][0] else None
        last_single = components['last_names'][1] if len(components['last_names']) > 1 else components['last_names'][0]
        last_combined = components['last_names'][0].replace('-', '') if last_hyphenated else last_single
        
        # Variant 1: First part + Last part (Paul + Bregieira)
        variants.append(first_single.lower() + last_single.lower())
        variants.append(first_single.capitalize() + last_single.capitalize())
        variants.append(first_single.upper() + last_single.lower())
        variants.append((first_single + last_single).capitalize())
        
        # Variant 2: Combined first + Last (PaulPhilipp + Bregieira) - if first was hyphenated
        if first_combined != first_single:
            variants.append(first_combined.lower() + last_single.lower())
            variants.append(first_combined.capitalize() + last_single.capitalize())
            variants.append(first_combined.upper() + last_single.lower())
            variants.append((first_combined + last_single).capitalize())
        
        # Variant 3: Hyphenated first + Last (Paul-Philipp + Bregieira)
        if first_hyphenated:
            variants.append(first_hyphenated.lower() + last_single.lower())
            variants.append(first_hyphenated.capitalize() + last_single.capitalize())
            variants.append(first_hyphenated.upper() + last_single.lower())
            variants.append((first_hyphenated + last_single).capitalize())
        
        # Variant 4: First + Combined last (if last was hyphenated)
        if last_combined != last_single:
            variants.append(first_single.lower() + last_combined.lower())
            variants.append(first_single.capitalize() + last_combined.capitalize())
            variants.append(first_single.upper() + last_combined.lower())
            variants.append((first_single + last_combined).capitalize())
        
        # Variant 5: First + Hyphenated last (PRESERVE HYPHEN in last)
        if last_hyphenated:
            variants.append(first_single.lower() + last_hyphenated.lower())
            variants.append(first_single.capitalize() + last_hyphenated.capitalize())
            variants.append(first_single.upper() + last_hyphenated.lower())
            variants.append((first_single + last_hyphenated).capitalize())
    
    # 3. FIRST INITIAL + LAST
    if components['first_names'] and components['last_names']:
        first_main = components['first_names'][1] if len(components['first_names']) > 1 else components['first_names'][0]
        last_main = components['last_names'][1] if len(components['last_names']) > 1 else components['last_names'][0]
        
        if first_main:
            initial_upper = first_main[0].upper()
            initial_lower = first_main[0].lower()
            last_clean = last_main.replace('-', '')
            
            variants.append(initial_upper + last_clean.capitalize())
            variants.append(initial_lower + last_clean.lower())
    
    # 4. FULL NAME (first + middle + last)
    if components['middle_names'] and components['last_names'] and components['first_names']:
        first_single = components['first_names'][1] if len(components['first_names']) > 1 else components['first_names'][0]
        first_combined = components['first_names'][0].replace('-', '') if '-' in components['first_names'][0] else first_single
        middle_main = components['middle_names'][0]
        last_main = components['last_names'][1] if len(components['last_names']) > 1 else components['last_names'][0]
        
        middle_clean = middle_main.replace('-', '')
        last_clean = last_main.replace('-', '')
        
        # Version 1: First part only
        full = first_single + middle_clean + last_clean
        if len(full) <= 20:
            variants.append(full.lower())
            variants.append(first_single.capitalize() + middle_clean.capitalize() + last_clean.capitalize())
            variants.append(first_single.upper() + middle_clean.lower() + last_clean.lower())
            variants.append(full.capitalize())
        
        # Version 2: Combined first (if hyphenated)
        if first_combined != first_single:
            full_combined = first_combined + middle_clean + last_clean
            if len(full_combined) <= 20:
                variants.append(full_combined.lower())
                variants.append(first_combined.capitalize() + middle_clean.capitalize() + last_clean.capitalize())
                variants.append(first_combined.upper() + middle_clean.lower() + last_clean.lower())
                variants.append(full_combined.capitalize())
    
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for v in variants:
        if v not in seen and v:
            seen.add(v)
            result.append(v)
    
    return result

# -------------------------
# Date variants
# -------------------------
def date_variants(d):
    """
    Generate date variants from a datetime object.
    Formats:
        - DDMMYYYY, MMDDYYYY
        - DDMMYY, MMDDYY
        - YYYY, YY
    """
    if not d:
        return []

    day = str(d.day)
    day_padded = f"{d.day:02d}"

    month = str(d.month)
    month_padded = f"{d.month:02d}"

    year_full = str(d.year)
    year_short = year_full[-2:]

    variants = []

    # Most common formats first
    variants.append(day_padded + month_padded + year_full) 
    variants.append(day + month + year_full)                 

    variants.append(day_padded + month_padded + year_short)  
    variants.append(day + month + year_short)                

    # Month-first (US)
    variants.append(month_padded + day_padded + year_full)   
    variants.append(month + day + year_full)

    variants.append(month_padded + day_padded + year_short)
    variants.append(month + day + year_short)

    # Only year
    variants.append(year_full)
    variants.append(year_short)

    return dedupe(variants)

# -------------------------
# Special characters
# -------------------------
def special_chars_variants(word):
    """
    Generate variants of a word with special characters
    at the beginning, end, and both.
    """
    variants = [word]
    for c in SPECIAL_CHARS:
        variants.append(c + word)
        variants.append(word + c)
        variants.append(c + word + c)
    return variants

# -------------------------
# Common numbers
# -------------------------
def append_common_numbers(word):
    COMMON_NUMBERS = ["1", "123", "1234", "69", "7", "17", "123456"]
    return [word + n for n in COMMON_NUMBERS]

# ---------------------------------------------------------
# RELATIONS + CHILDREN
# ---------------------------------------------------------

def process_person_for_combinations(person, target_last, target_name_variants, target_dates):
    """
    Process relations or children.
    """
    
    all_words = []

    # --- nome ---
    raw_name = person.get("name", "")
    if not raw_name:
        return None, []

    components = parse_name_components(raw_name)
    
    if not components['all_parts']:
        return None, []

    person_last_variants = components['last_names']
    person_last_main = person_last_variants[0].lower() if person_last_variants else ""
    
    if person_last_main == target_last.lower():
        filtered_parts = components['first_names'] + components['middle_names']
        if not filtered_parts:
            return None, []
        clean_name = " ".join(filtered_parts)
    else:
        clean_name = " ".join(components['all_parts'])
    
    name_vars = name_variants(clean_name)

    # --- nickname ---
    nickname = person.get("nickname")
    nickname_vars = toggle_case(sanitize_word(nickname)) if nickname else []

    # --- dates ---
    person_dates = date_variants(person.get("birth")) if person.get("birth") else []

    all_words += name_vars
    
    for n in name_vars[:5]:
        for dt in (person_dates + target_dates)[:3]:
            all_words.append(n + dt)

    all_words += nickname_vars
    for nn in nickname_vars[:3]:
        for dt in (person_dates + target_dates)[:3]:
            all_words.append(nn + dt)

    processed = {
        "name_vars": name_vars[:10],
        "nickname_vars": nickname_vars[:5],
        "dates": person_dates[:5]
    }

    return processed, all_words

# -------------------------
# PETS
# -------------------------
def process_pet_for_combinations(pet, target_name_variants, target_dates):
    """
    Generate variants for pets.
    """
    all_words = []

    raw_name = pet.get("name", "")
    if not raw_name:
        return None, []

    components = parse_name_components(raw_name)
    
    if not components['all_parts']:
        return None, []

    clean_name = " ".join(components['all_parts'])
    name_vars = name_variants(clean_name)

    nickname = pet.get("nickname")
    nickname_vars = toggle_case(sanitize_word(nickname)) if nickname else []

    pet_dates = date_variants(pet.get("birth")) if pet.get("birth") else []

    all_words += name_vars[:5]
    all_words += nickname_vars[:3]

    for tn in target_name_variants[:3]:
        for nv in name_vars[:2]:
            all_words.append(tn + nv)
            all_words.append(nv + tn)
            
            if target_dates:
                all_words.append(tn + nv + target_dates[0])

    processed = {
        "name_vars": name_vars[:5],
        "nickname_vars": nickname_vars[:3],
        "dates": pet_dates[:3]
    }

    return processed, all_words

# -------------------------
# Combos between pets
# -------------------------
def combine_pets(processed_pets):
    """
    Combine names between pets.
    """
    if len(processed_pets) < 2:
        return []
    
    pet_words = []
    for p1, p2 in itertools.islice(itertools.permutations(processed_pets, 2), 4):
        n1 = p1["name_vars"][0] if p1["name_vars"] else None
        n2 = p2["name_vars"][0] if p2["name_vars"] else None
        if n1 and n2:
            pet_words.append(n1 + n2)
    
    return pet_words


# -------------------------
# Helper-driven Wordlist generation
# -------------------------

def _collect_target_variants(profile):
    return name_variants(profile.name) if profile.name else []


def _collect_important_words(profile, normalized_name_variants):
    words = []
    for kw in profile.keywords:
        if kw:
            words += toggle_case(sanitize_word(normalize_string(kw)))
    words = dedupe(words)
    return words


def _collect_dates(profile):
    date_list = []
    if profile.birth:
        date_list += date_variants(profile.birth)
    for d in profile.important_dates:
        date_list += date_variants(d)
    return dedupe(date_list)


def _process_people(list_of_people, target_last, target_name_variants, date_list):
    words = []
    processed = []
    for person in list_of_people:
        pproc, pwords = process_person_for_combinations(person, target_last, target_name_variants, date_list)
        if not pproc:
            continue
        processed.append(pproc)
        words += pwords
        for dt in pproc.get("dates", []):
            if dt not in date_list:
                date_list.append(dt)
        print(f"[+] Processed person: {person.get('name','(unnamed)')} — added {len(pwords)} words")
    return processed, words


def _process_pets(pets, target_name_variants, date_list):
    words = []
    processed = []
    for pet in pets:
        pproc, pwords = process_pet_for_combinations(pet, target_name_variants, date_list)
        if not pproc:
            continue
        processed.append(pproc)
        words += pwords
        for dt in pproc.get("dates", []):
            if dt not in date_list:
                date_list.append(dt)
        print(f"[+] Processed pet: {pet.get('name','(unnamed)')} — added {len(pwords)} words")
    return processed, words


def _combine_entity_date_combos(all_entities, date_list):
    combos = []
    for entity in all_entities[:15]:
        for dtv in date_list:
            combos.append(entity + dtv)
            combos.append(dtv + entity)
    return combos


def _apply_final_transforms(words, profile):
    
    # -------------------------
    # COMMON NUMBERS
    # -------------------------
    if getattr(profile, "common_numbers_enabled", True):
        for w in list(words):
            words += append_common_numbers(w)
        print(f"[+] After appending common numbers: {len(words)} items")

    # -------------------------
    # SPECIAL CHARACTERS
    # -------------------------
    final_words = []

    if getattr(profile, "special_enabled", True):
        for w in words:
            final_words += special_chars_variants(w)
        print(f"[+] After applying special characters variants: {len(final_words)} items")
    else:
        final_words = list(words)

    # -------------------------
    # LEET
    # -------------------------

    if getattr(profile, "leet_enabled", False):
        leet_words = []
        for w in final_words:
            leet_words += apply_leet(w)
        final_words += leet_words
        print(f"[+] After applying leet transformations: {len(final_words)} items")

    # -------------------------
    # DEDUPE
    # -------------------------

    final_words = dedupe(final_words)
    print(f"[+] After deduplication: {len(final_words)} unique items")
    
    filtered = []
    for w in final_words:
        if len(w) < MIN_WORDLIST_LENGTH:
            continue
        if w.isdigit():
            continue
        if all(c in SPECIAL_CHARS for c in w):
            continue
        if all_upper(w):
            continue
        filtered.append(w)

    return filtered


def generate_wordlist(profile):
    print("[+] Starting wordlist generation...")
    
    target_name_variants = _collect_target_variants(profile)
    print(f"[+] Target name variants: {len(target_name_variants)}")

    important_words = _collect_important_words(profile, [])
    print(f"[+] Important words (keywords): {len(important_words)}")

    date_list = _collect_dates(profile)
    print(f"[+] Date variants collected: {len(date_list)}")

    target_components = parse_name_components(profile.name) if profile.name else {'last_names': [], 'first_names': []}
    target_last = target_components['last_names'][0] if target_components['last_names'] else ""
    target_first = target_components['first_names'][0] if target_components['first_names'] else ""

    processed_relations, relation_words = _process_people(
        profile.relationships, 
        target_last, 
        target_name_variants[:5],
        date_list
    )
    print(f"[+] Relations processed: {len(processed_relations)} — relation words {len(relation_words)}")

    processed_children, children_words = _process_people(
        profile.children, 
        target_last, 
        target_name_variants[:5], 
        date_list
    )
    print(f"[+] Children processed: {len(processed_children)} — children words {len(children_words)}")
    
    child_combo_count = 0
    for c1, c2 in itertools.islice(itertools.permutations(processed_children, 2), 6):
        v1 = c1.get("name_vars", [])[0] if c1.get("name_vars") else None
        v2 = c2.get("name_vars", [])[0] if c2.get("name_vars") else None
        if v1 and v2:
            children_words.append(v1 + v2)
            child_combo_count += 1

    processed_pets, pet_words = _process_pets(
        profile.pets, 
        target_name_variants[:5], 
        date_list
    )
    print(f"[+] Pets processed: {len(processed_pets)} — pet words {len(pet_words)}")
    pet_combo_words = combine_pets(processed_pets)
    pet_words += pet_combo_words

    words = []
    words += target_name_variants
    words += important_words
    words += relation_words
    words += children_words
    words += pet_words
    print(f"[+] Accumulated base words: {len(words)}")

    combo_count = 0
    for w in important_words[:3]:
        for tn in target_name_variants[:3]:
            words.append(tn + w)
            words.append(w + tn)
            combo_count += 2

    rel_combo_count = 0
    for rel in processed_relations[:2]:
        for tn in target_name_variants[:2]:
            for rv in (rel.get("name_vars", []) + rel.get("nickname_vars", []))[:2]:
                words.append(tn + rv)
                words.append(rv + tn)
                rel_combo_count += 2

    # First name + date + last name combinations
    if target_first and target_last and date_list:
        # Collect ALL first name variants (hyphenated + individual parts)
        first_variants = []
        if target_components['first_names']:
            for fname in target_components['first_names']:
                if '-' in fname:
                    # Add hyphenated versions
                    hyphen_parts = fname.split('-')
                    first_variants.append(fname.lower())
                    first_variants.append('-'.join([p.capitalize() for p in hyphen_parts]))
                    first_variants.append(hyphen_parts[0].capitalize() + '-' + hyphen_parts[1].lower())
                    first_variants.append(fname.upper())
                else:
                    # Add individual parts
                    first_variants.append(fname.lower())
                    first_variants.append(fname.capitalize())
                    first_variants.append(fname.upper())
        
        # Collect ALL last name variants (hyphenated + individual parts)
        last_variants = []
        if target_components['last_names']:
            for lname in target_components['last_names']:
                if '-' in lname:
                    # Add hyphenated versions
                    hyphen_parts = lname.split('-')
                    last_variants.append(lname.lower())
                    last_variants.append('-'.join([p.capitalize() for p in hyphen_parts]))
                    last_variants.append(hyphen_parts[0].capitalize() + '-' + hyphen_parts[1].lower())
                    
                    # Also add non-hyphenated combined version
                    combined = lname.replace('-', '')
                    last_variants.append(combined.lower())
                    last_variants.append(combined.capitalize())
                else:
                    # Add individual parts
                    last_variants.append(lname.lower())
                    last_variants.append(lname.capitalize())
        
        # Remove duplicates
        first_variants = list(dict.fromkeys(first_variants))
        last_variants = list(dict.fromkeys(last_variants))
        
        # Generate combinations
        for fv in first_variants:
            for dt in date_list:
                for lv in last_variants:
                    words.append(fv + dt + lv)
        
        # Combinations with dates
        if profile.birth:
            year_full = str(profile.birth.year)
            year_short = year_full[-2:]

            day_variants = [
                str(profile.birth.day),
                f"{profile.birth.day:02d}"
            ]

            month_variants = [
                str(profile.birth.month),
                f"{profile.birth.month:02d}"
            ]

            # First name + year
            for fv in first_variants:
                words.append(fv + year_full)
                words.append(fv + year_short)

            # Last name + year
            for lv in last_variants:
                words.append(lv + year_full)
                words.append(lv + year_short)

            # First + Last + year
            for fv in first_variants[:5]:
                for lv in last_variants[:5]:
                    words.append(fv + lv + year_full)
                    words.append(fv + lv + year_short)

            # First name + date variants
            for fv in first_variants:
                for d in day_variants:
                    words.append(fv + d)              # Marcelo7 / Marcelo07

                    words.append(fv + d + year_short) # Marcelo793 / Marcelo0793

                    for m in month_variants:
                        words.append(fv + d + m)           # Marcelo710 / Marcelo0710
                        words.append(fv + d + m + year_short) # Marcelo71093
                        words.append(fv + d + m + year_full)  # Marcelo07101993

                for m in month_variants:
                    words.append(fv + m)                 # Marcelo10
                    words.append(fv + m + year_short)    # Marcelo1093
                    words.append(fv + m + year_full)     # Marcelo101993

    limited_entities = target_name_variants[:5] + important_words[:3]
    for rel in processed_relations[:2]:
        limited_entities += rel.get("name_vars", [])[:2]
    for child in processed_children[:2]:
        limited_entities += child.get("name_vars", [])[:2]
    
    limited_entities = dedupe(limited_entities)[:15]
    date_combos = _combine_entity_date_combos(limited_entities, date_list)
    words += date_combos
    print(f"[+] Added date combos: total words now {len(words)}")

    words = dedupe(words)
    print(f"[+] After deduplication before transforms: {len(words)}")

    filtered = _apply_final_transforms(words, profile)
    print(f"[+] Final filtered wordlist size: {len(filtered)}")

    return filtered, len(filtered)

# -------------------------
# PIN GENERATION
# -------------------------

def _extract_pins_from_date(d):
    if not d:
        return []
    
    day_padded = f"{d.day:02d}"
    month_padded = f"{d.month:02d}"
    day_single = str(d.day)
    month_single = str(d.month)
    year = str(d.year)
    year_short = year[-2:]
    
    variants = []
    
    variants.append(day_padded + month_padded)
    variants.append(day_single + month_single)
    variants.append(day_padded + month_padded + year_short)
    variants.append(day_single + month_single + year_short)
    variants.append(day_padded + month_padded + year)
    variants.append(day_single + month_single + year)
    
    variants.append(month_padded + day_padded)
    variants.append(month_single + day_single)
    variants.append(month_padded + day_padded + year_short)
    variants.append(month_single + day_single + year_short)
    variants.append(month_padded + day_padded + year)
    variants.append(month_single + day_single + year)
    
    variants.append(day_padded + year_short)
    variants.append(day_single + year_short)
    variants.append(month_padded + year_short)
    variants.append(month_single + year_short)
    variants.append(day_padded + year)
    variants.append(day_single + year)
    variants.append(month_padded + year)
    variants.append(month_single + year)
    
    variants.append(year)
    variants.append(year_short)
    
    seen = set()
    result = []
    for v in variants:
        if v.isdigit() and v not in seen:
            seen.add(v)
            result.append(v)
    
    return result

def _collect_date_based_pins(profile, length):
    pins = []
    seen = set()
    
    def add_pins(date_obj):
        for pin in _extract_pins_from_date(date_obj):
            if len(pin) == int(length) and pin not in seen:
                pins.append(pin)
                seen.add(pin)
    
    if profile.birth:
        add_pins(profile.birth)
    
    for d in profile.important_dates:
        add_pins(d)
    
    for rel in profile.relationships:
        if rel.get("birth"):
            add_pins(rel["birth"])
    
    for child in profile.children:
        if child.get("birth"):
            add_pins(child["birth"])
    
    for pet in profile.pets:
        if pet.get("birth"):
            add_pins(pet["birth"])
    
    return pins


def _add_t9_variants(s, length, t9_single, t9_multi):
    if not s:
        return
    
    cleaned = sanitize_word(s)
    if not cleaned:
        return
    
    single = string_to_t9(cleaned)
    multi = string_to_t9_multi(cleaned)
    
    if single and len(single) == int(length) and single.isdigit():
        t9_single.add(single)
    if multi and len(multi) == int(length) and multi.isdigit():
        t9_multi.add(multi)

def _collect_t9_pins(profile, length):
    t9_single = set()
    t9_multi = set()
    
    _add_t9_variants(profile.name, length, t9_single, t9_multi)
    
    for kw in profile.keywords:
        _add_t9_variants(kw, length, t9_single, t9_multi)
    
    for em in profile.emails:
        if em:
            _add_t9_variants(em.split("@")[0], length, t9_single, t9_multi)
    
    for rel in profile.relationships:
        _add_t9_variants(rel.get("name"), length, t9_single, t9_multi)
        _add_t9_variants(rel.get("nickname"), length, t9_single, t9_multi)
    
    for child in profile.children:
        _add_t9_variants(child.get("name"), length, t9_single, t9_multi)
        _add_t9_variants(child.get("nickname"), length, t9_single, t9_multi)
    
    for pet in profile.pets:
        _add_t9_variants(pet.get("name"), length, t9_single, t9_multi)
        _add_t9_variants(pet.get("nickname"), length, t9_single, t9_multi)
    
    return sorted(t9_single), sorted(t9_multi)

def _extract_numeric_sequences(s, length):
    if not s:
        return []
    
    numbers = re.findall(r'\d+', s)
    
    sequences = []
    for num in numbers:
        if len(num) == int(length):
            sequences.append(num)
        elif len(num) > int(length):
            for i in range(len(num) - int(length) + 1):
                sequences.append(num[i:i+int(length)])
    
    return sequences

def _collect_numeric_pins(profile, length):
    numeric_pins = []
    seen = set()
    
    for em in profile.emails:
        if em:
            for pin in _extract_numeric_sequences(em, length):
                if pin not in seen:
                    numeric_pins.append(pin)
                    seen.add(pin)
            username = em.split("@")[0]
            for pin in _extract_numeric_sequences(username, length):
                if pin not in seen:
                    numeric_pins.append(pin)
                    seen.add(pin)
    
    for kw in profile.keywords:
        if kw:
            for pin in _extract_numeric_sequences(kw, length):
                if pin not in seen:
                    numeric_pins.append(pin)
                    seen.add(pin)
    
    if profile.name:
        for pin in _extract_numeric_sequences(profile.name, length):
            if pin not in seen:
                numeric_pins.append(pin)
                seen.add(pin)
    
    return numeric_pins

def _known_patterns(length):
    n = int(length)
    patterns = []
    
    if n <= 9:
        inc = ''.join(str(i) for i in range(1, n+1))
    else:
        inc = ''.join(str(i % 10) for i in range(1, n+1))
    patterns.append(inc)
    
    patterns.append(inc[::-1])
    
    for d in range(10):
        patterns.append(str(d) * n)
    
    if n == 4:
        patterns.insert(0, '2580')
        patterns.insert(1, '0852')
    
    if n == 6:
        patterns.extend(['123654', '456321', '456987', '789654', 
                        '147258', '852741', '369258', '258963'])
    
    return [p for p in patterns if p.isdigit() and len(p) == n]


def _load_base_pin_file(base_file, length):
    if base_file.exists():
        return _read_base_file(base_file)
    
    print(f"[!] Base PIN file not found: {base_file.name}.")
    print("[!] You can create it yourself. Example command:")
    print(f"    hashcat -a 3 {'?d'*int(length)} --stdout > {base_file.name}")
    
    resp = input(f"[?] Do you want MagicGuess to create {base_file.name} now? (y/N): ").strip().lower()
    if resp not in ("y", "yes"):
        print("[!] Skipping base file creation. Using generated PINs only.")
        return []
    
    return _create_base_file(base_file, length)


def _read_base_file(base_file):
    try:
        raw = base_file.read_bytes()
        encoding = _detect_encoding(raw)
        text = raw.decode(encoding)
        base_list = [ln.strip() for ln in text.splitlines() if ln.strip()]
        print(f"[+] Loaded base PIN list from {base_file.name} ({len(base_list)} entries) using encoding {encoding}")
        return base_list
    except Exception as e:
        print(f"[!] Failed to read {base_file.name}: {e}")
        return []


def _detect_encoding(raw):
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    elif raw.startswith(b"\xff\xfe"):
        return "utf-16"
    elif raw.startswith(b"\xfe\xff"):
        return "utf-16-be"
    
    for encoding in ["utf-8", "utf-16", "latin-1"]:
        try:
            raw.decode(encoding)
            return encoding
        except Exception:
            continue
    return "latin-1"


def _create_base_file(base_file, length):
    total = 10 ** int(length)
    WARN_LIMIT = 2_000_000
    
    if total > WARN_LIMIT:
        confirm = input(f"[!] This will create {total:,} lines (large file). Continue? (y/N): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("[!] Skipping automatic creation. Using generated PINs only.")
            return []
    
    print(f"[+] Creating {base_file.name} with {total:,} entries...")
    with base_file.open("w", encoding="utf-8") as fh:
        for i in range(total):
            fh.write(str(i).zfill(int(length)) + "\n")
            if i > 0 and i % 1000000 == 0:
                print(f"  wrote {i:,} lines...")
    
    print(f"[+] Created {base_file.name}")
    with base_file.open("r", encoding="utf-8") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


def _build_final_pinlist(date_pins, numeric_pins, t9_single, t9_multi, base_list, length):
    final = []
    seen = set()
    
    for p in date_pins:
        if p not in seen:
            final.append(p)
            seen.add(p)
    
    for p in numeric_pins:
        if p not in seen:
            final.append(p)
            seen.add(p)
    
    for p in t9_single:
        if p not in seen:
            final.append(p)
            seen.add(p)
    
    for p in t9_multi:
        if p not in seen:
            final.append(p)
            seen.add(p)
    
    for p in _known_patterns(length):
        if p not in seen:
            final.append(p)
            seen.add(p)
    
    for p in base_list:
        if p.isdigit() and len(p) == int(length) and p not in seen:
            final.append(p)
            seen.add(p)
    
    return final


def generate_pinlist(profile, length=4):
    date_pins = _collect_date_based_pins(profile, length)
    numeric_pins = _collect_numeric_pins(profile, length)
    t9_single, t9_multi = _collect_t9_pins(profile, length)
    
    base_file = Path(__file__).parent / f"PIN{length}_markov.txt"
    base_list = _load_base_pin_file(base_file, length)
    
    final = _build_final_pinlist(date_pins, numeric_pins, t9_single, t9_multi, base_list, length)
    
    print(f"[+] Generated {len(date_pins)} date-based PINs; "
          f"{len(numeric_pins)} numeric sequences; "
          f"T9(single) {len(t9_single)}; T9(multi) {len(t9_multi)}; "
          f"final PINlist length: {len(final)}")
    
    return final, len(final)