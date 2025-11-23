# generators.py

from magicguess.utils import sanitize_word, dedupe, normalize_string, all_upper
from datetime import datetime
import itertools

SPECIAL_CHARS = ['!', '@', '#', '$', '%', '&', '*', '"']
COMMON_NUMBERS = ["1", "12", "123", "1234", "69", "7", "17", "123456"]
MIN_LENGTH = 6

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
    """Applies simple substitutions, only 1 letter at a time, without explosion."""
    variants = set([word])

    for idx, ch in enumerate(word.lower()):
        if ch in LEET_MAP:
            for sub in LEET_MAP[ch]:
                new_word = list(word)
                new_word[idx] = sub
                variants.add("".join(new_word))

    return list(variants)


# -------------------------
# Toggle case of individual words
# -------------------------
def toggle_case(word):
    return list(dedupe([
        word.lower(),
        word.capitalize(),
        word.upper() if len(word) > 1 else word.upper()
    ]))

# -------------------------
# Name variants
# -------------------------
def name_variants(full_name: str):
    """
    Generates variations:
      - individual toggles of each part (first, middle(s), last)
      - compound combinations ONLY if they include the first name or the first initial
      - includes initial+middle+last variant (e.g., MDinisBregieira)
      - avoids combos that are only middle+last (to prevent explosion)
    """
    parts_raw = [p for p in full_name.strip().split() if p]
    parts = [sanitize_word(p) for p in parts_raw]
    if not parts:
        return []

    # toggles per part (list of lists)
    toggles_per_part = [toggle_case(p) for p in parts]

    # 1) Simple variants: all individual toggles (first, middle(s), last)
    simple_names = list(itertools.chain.from_iterable(toggles_per_part))

    # 2) Compound combinations — only combos that include part 0 (first)
    combined = []
    # Cartesian product of toggles (generates combos with all parts)
    for combo in itertools.product(*toggles_per_part):
        combined_entry = ''.join(combo)
        combined.append(combined_entry)

    # 3) Also include first+last only (skip middles) — but using toggles:
    if len(parts) >= 2:
        first_toggles = toggles_per_part[0]
        last_toggles = toggles_per_part[-1]
        for f in first_toggles:
            for l in last_toggles:
                combined.append(f + l)

    # 4) Include initial(first) + middle(s) + last (if there are >=3 parts or even with 2 parts the initial+last is allowed)
    first_initials = []
    first_raw = parts[0]
    if first_raw:
        fi_lower = first_raw[0].lower()
        fi_cap = first_raw[0].upper()
        first_initials = [fi_lower, fi_cap]

    if len(parts) >= 2:
        # build combos where first replaced by its initial and the rest follow with their toggles
        # toggles for middle(s) and last:
        if len(parts) == 2:
            # initial + last
            for init in first_initials:
                for l in toggles_per_part[-1]:
                    combined.append(init + l)
        else:
            # initial + middle(s) + last
            middle_toggles_product = list(itertools.product(*toggles_per_part[1:]))  # includes middle(s) + last
            for init in first_initials:
                for mid_combo in middle_toggles_product:
                    combined.append(init + ''.join(mid_combo))

    # 5) Deduplicate and return: include simple_names and combined (but filter out unwanted middle+last-only combos)
    # Filter rule: remove any combined that starts with a middle part (i.e., does not start with any toggle of the first or first initial)
    allowed_prefixes = set(toggles_per_part[0])  # e.g. {'marcelo','Marcelo','marcelO'}
    allowed_prefixes.update([parts[0][0].lower(), parts[0][0].upper()])  # add initials 'm' and 'M'

    filtered_combined = []
    for c in combined:
        # check if c starts with any allowed prefix:
        if any(c.startswith(pref) for pref in allowed_prefixes):
            filtered_combined.append(c)
        else:
            # ignore combos that do not start with first or initial (this excludes middle+last)
            continue

    result = dedupe(simple_names + filtered_combined)

    return result

# -------------------------
# Date variants
# -------------------------
def date_variants(d):
    if not d:
        return []

    days = [str(d.day), f"{d.day:02d}"]
    months = [str(d.month), f"{d.month:02d}"]
    year_full = str(d.year)
    year_short = year_full[-2:]

    variants = set()
    for day in days:
        for month in months:
            for year in [year_full, year_short]:
                variants.add(f"{day}{month}{year}")
                variants.add(f"{month}{day}{year}")  # inverted

    variants.add(year_full)
    variants.add(year_short)

    return list(dedupe(variants))

# -------------------------
# Special characters
# -------------------------
def special_chars_variants(word):
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
    return [word + n for n in COMMON_NUMBERS]

# ---------------------------------------------------------
# RELATIONS + CHILDREN (unified structure)
# ---------------------------------------------------------

def process_person_for_combinations(person, target_last, target_name_variants, target_dates):
    """Process relations or children: remove duplicate nickname, generate variants,
       and return processed structure + own wordlist."""
    
    all_words = []

    # --- nome ---
    raw_name = person.get("name", "")
    if not raw_name:
        return None, []

    parts_raw = [p for p in raw_name.strip().split() if p]
    parts = [sanitize_word(p) for p in parts_raw]

    person_last = parts[-1].lower() if parts else ""

    # remove nickname if equal to target's last name
    if person_last == target_last:
        parts = parts[:-1]

    if not parts:
        return None, []

    clean_name = " ".join(parts)
    name_vars = name_variants(clean_name)

    # --- nickname ---
    nickname = person.get("nickname")
    nickname_vars = toggle_case(sanitize_word(nickname)) if nickname else []

    # --- dates ---
    person_dates = date_variants(person.get("birth")) if person.get("birth") else []

    # --- isolated variants ---
    all_words += name_vars
    for n in name_vars:
        for dt in person_dates + target_dates:
            all_words.append(n + dt)

    all_words += nickname_vars
    for nn in nickname_vars:
        for dt in person_dates + target_dates:
            all_words.append(nn + dt)

    processed = {
        "name_vars": name_vars,
        "nickname_vars": nickname_vars,
        "dates": person_dates
    }

    return processed, all_words

# -------------------------
# PETS
# -------------------------
def process_pet_for_combinations(pet, target_name_variants, target_dates):
    """
    Generate variants for pets:
      - Name of the pet
      - Nickname of the pet
      - Combos target <-> pet
      - Combos between pets (without dates)
    """
    all_words = []

    raw_name = pet.get("name", "")
    if not raw_name:
        return None, []

    parts_raw = [p for p in raw_name.strip().split() if p]
    parts = [sanitize_word(p) for p in parts_raw]

    if not parts:
        return None, []

    clean_name = " ".join(parts)
    name_vars = name_variants(clean_name)

    nickname = pet.get("nickname")
    nickname_vars = toggle_case(sanitize_word(nickname)) if nickname else []

    pet_dates = date_variants(pet.get("birth")) if pet.get("birth") else []

    # --- Isolated words of the pet ---
    all_words += name_vars
    all_words += nickname_vars

    # --- Combos target <-> pet ---
    for tn in target_name_variants:
        for nv in name_vars:
            # target+pet
            all_words.append(tn + nv)
            all_words.append(nv + tn)
            # with dates: only one date per combination
            for dt in target_dates + pet_dates:
                all_words.append(tn + nv + dt)
                all_words.append(nv + tn + dt)

        for nn in nickname_vars:
            # target+nickname
            all_words.append(tn + nn)
            all_words.append(nn + tn)
            # with dates
            for dt in target_dates + pet_dates:
                all_words.append(tn + nn + dt)
                all_words.append(nn + tn + dt)

    processed = {
        "name_vars": name_vars,
        "nickname_vars": nickname_vars,
        "dates": pet_dates
    }

    return processed, all_words

# -------------------------
# Combos between pets
# -------------------------
def combine_pets(processed_pets):
    """
    Combine names/nicknames between pets.
    NEVER use dates or create passwords with only dates.
    """
    pet_words = []
    for p1, p2 in itertools.permutations(processed_pets, 2):
        for n1 in p1["name_vars"] + p1["nickname_vars"]:
            for n2 in p2["name_vars"] + p2["nickname_vars"]:
                pet_words.append(n1 + n2)
    return pet_words


# -------------------------
# Wordlist generation
# -------------------------
def generate_wordlist(profile):
    words = []

    # Nomes do target
    target_name_variants = name_variants(profile.name) if profile.name else []
    words += target_name_variants

    # Palavras importantes
    for kw in profile.keywords:
        if kw:
            words += toggle_case(sanitize_word(normalize_string(kw)))
    words = dedupe(words)

    # Target and important dates
    date_list = []
    if profile.birth:
        date_list += date_variants(profile.birth)
    for d in profile.important_dates:
        date_list += date_variants(d)
    date_list = dedupe(date_list)

    important_words = words.copy()
    target_last = sanitize_word(profile.name.strip().split()[-1]).lower() if profile.name else []

    # ------------------- RELATIONS -------------------------
    relation_words = []
    processed_relations = []
    for rel in profile.relationships:
        processed, words_alone = process_person_for_combinations(rel, target_last, target_name_variants, date_list)
        if not processed:
            continue
        processed_relations.append(processed)
        relation_words += words_alone

        # Combos target <-> relation/nickname
        for tn in target_name_variants:
            for rv in processed["name_vars"]:
                relation_words += [tn + rv, rv + tn]
                for dt in date_list + processed["dates"]:
                    relation_words += [tn + rv + dt, rv + tn + dt]
            for nn in processed["nickname_vars"]:
                relation_words += [tn + nn, nn + tn]
                for dt in date_list + processed["dates"]:
                    relation_words += [tn + nn + dt, nn + tn + dt]

    # ------------------- CHILDREN -------------------------
    children_words = []
    processed_children = []
    for child in profile.children:
        processed, words_alone = process_person_for_combinations(child, target_last, target_name_variants, date_list)
        if not processed:
            continue
        processed_children.append(processed)
        children_words += words_alone

        # Combos target <-> child/nickname
        for tn in target_name_variants:
            for cv in processed["name_vars"]:
                children_words += [tn + cv, cv + tn]
                for dt in date_list + processed["dates"]:
                    children_words += [tn + cv + dt, cv + tn + dt]
            for nn in processed["nickname_vars"]:
                children_words += [tn + nn, nn + tn]
                for dt in date_list + processed["dates"]:
                    children_words += [tn + nn + dt, nn + tn + dt]

    # Combos between children (without dates)
    for c1, c2 in itertools.permutations(processed_children, 2):
        for v1 in c1["name_vars"]:
            for v2 in c2["name_vars"]:
                children_words.append(v1 + v2)

    words += relation_words + children_words

    # ------------------- PETS -------------------------
    pet_words = []
    processed_pets = []

    for pet in profile.pets:
        processed, words_alone = process_pet_for_combinations(pet, target_name_variants, date_list)
        if not processed:
            continue
        processed_pets.append(processed)
        pet_words += words_alone

    pet_words += combine_pets(processed_pets)
    # --- Variantes of pets with dates ---
    for pet in processed_pets:
        for nv in pet["name_vars"] + pet["nickname_vars"]:
            for dt in pet["dates"]:
                # adicionar nv + dt
                pet_words.append(nv + dt)
                # aplicar números comuns
                for n in COMMON_NUMBERS:
                    pet_words.append(nv + dt + n)
                # aplicar caracteres especiais
                for c in SPECIAL_CHARS:
                    pet_words.append(nv + dt + c)
                    pet_words.append(c + nv + dt)
                    pet_words.append(c + nv + dt + c)

    words += pet_words

    # ------------------- IMPORTANT WORDS -------------------------

    # -------------------------
    # Combos target <-> important words
    # -------------------------
    important_combos = []
    for w in important_words:
        for tn in target_name_variants:
            important_combos.append(tn + w)
            important_combos.append(w + tn)

    words += important_combos

    # -------------------------
    # Combos target <-> relationships
    # -------------------------
    relation_combos = []
    for rel in processed_relations:
        for tn in target_name_variants:
            for rv in rel["name_vars"] + rel["nickname_vars"]:
                relation_combos.append(tn + rv)
                relation_combos.append(rv + tn)

    words += relation_combos

    # ------------------- IMPORTANT DATES -------------------------

    all_entities = []

    # Target
    all_entities += target_name_variants

    # Relations
    for rel in processed_relations:
        all_entities += rel["name_vars"] + rel["nickname_vars"]

    # Children
    for child in processed_children:
        all_entities += child["name_vars"] + child["nickname_vars"]

    # Pets
    for pet in processed_pets:
        all_entities += pet["name_vars"] + pet["nickname_vars"]

    # Important words
    all_entities += important_words

    # Combinações entity <-> date
    date_combos = []
    for entity in all_entities:
        for dtv in date_list:
            date_combos.append(entity + dtv)
            date_combos.append(dtv + entity)

    # Add to the wordlist
    words += date_combos


    # ------------------- COMMON NUMBERS -------------------------

    for w in important_words:
        words += append_common_numbers(w)

    # ------------------- SPECIAL CHARACTERS -------------------------

    final_words = []
    for w in words:
        final_words += special_chars_variants(w)

    # ------------------- LEET MODE -------------------------

    if profile.leet_enabled:
        leet_words = []
        for w in final_words:
            leet_words += apply_leet(w)
        final_words += leet_words

 
    # ------------------- DEDUPLICATION AND FILTERING -------------------------

    final_words = dedupe(final_words)
    filtered = []
    for w in final_words:
        if len(w) < MIN_LENGTH:
            continue
        if w.isdigit():
            continue
        if all(c in SPECIAL_CHARS for c in w):
            continue
        if all_upper(w):
            continue
        filtered.append(w)

    return filtered, len(filtered)

# -------------------------
# TODO: PIN list
# -------------------------
def generate_pinlist(profile):
    """
    PIN list simples:
    - Apenas datas do utilizador, relações e filhos
    - Apenas formatos de 4 e 6 dígitos: DDMM, MMYY, DDMMYY, MMDDYY
    - Nunca gerar só ano
    """
    pins = set()

    def extract_pins_from_date(d):
        if not d:
            return []

        day = f"{d.day:02d}"
        month = f"{d.month:02d}"
        year = str(d.year)
        year_short = year[-2:]

        variants = set()

        # 4 dígitos
        variants.add(day + month)       # DDMM
        variants.add(month + day)       # MMDD
        variants.add(month + year_short)  # MMYY
        variants.add(day + year_short)    # DDYY

        # 6 dígitos
        variants.add(day + month + year_short)  # DDMMYY
        variants.add(month + day + year_short)  # MMDDYY
        variants.add(day + month + year)        # DDMMYYYY (8 — opcional)
        variants.add(month + day + year)        # MMDDYYYY

        return variants

    # Datas do target
    if profile.birth:
        pins.update(extract_pins_from_date(profile.birth))

    for d in profile.important_dates:
        pins.update(extract_pins_from_date(d))

    # Datas das relações
    for rel in profile.relationships:
        if rel.get("birth"):
            pins.update(extract_pins_from_date(rel["birth"]))

    # Datas dos filhos
    for child in profile.children:
        if child.get("birth"):
            pins.update(extract_pins_from_date(child["birth"]))

    # filtro: PINs só numéricos
    clean_pins = sorted([p for p in pins if p.isdigit()])

    return clean_pins, len(clean_pins)
