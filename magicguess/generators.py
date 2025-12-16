# generators.py

from magicguess.utils import sanitize_word, dedupe, normalize_string, all_upper
from datetime import datetime
import itertools

SPECIAL_CHARS = ['!', '@', '#', '$', '%', '&', '*', '"']
MIN_WORDLIST_LENGTH = 6

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
    Applies substitutions, only 1 letter at a time to without explosion.
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

    # multi-press mapping (e.g. a=2, b=22, c=222)
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
# Toggle case of individual words
# -------------------------
def toggle_case(word):
    """
    Generate case toggles for a single word.
    """
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
    """
    Generate date variants from a datetime object.
    Formats:
        - DDMMYYYY, MMDDYYYY
        - DDMMYY, MMDDYY
        - YYYY, YY
    """
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
    # -------------------------------------------------------------------------
    # ADD COMMON NUMBERS AS YOU WISH - BE CAREFUL WITH EXPLOSION --------------
    COMMON_NUMBERS = ["1", "123", "1234", "69", "7", "17", "123456"]
    # -------------------------------------------------------------------------

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
# Helper-driven Wordlist generation (refactored)
# -------------------------

def _collect_target_variants(profile):
    return name_variants(profile.name) if profile.name else []


def _collect_important_words(profile, normalized_name_variants):
    words = []
    for kw in profile.keywords:
        if kw:
            words += toggle_case(sanitize_word(normalize_string(kw)))
    # include normalized name variants as important words base
    words = dedupe(words + normalized_name_variants)
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
            date_list.append(dt)
        # progress print per person
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
            date_list.append(dt)
        # progress print per pet
        print(f"[+] Processed pet: {pet.get('name','(unnamed)')} — added {len(pwords)} words")
    return processed, words


def _combine_entity_date_combos(all_entities, date_list):
    combos = []
    for entity in all_entities:
        for dtv in date_list:
            combos.append(entity + dtv)
            combos.append(dtv + entity)
    return combos


def _apply_final_transforms(words, profile):
    # apply common numbers
    for w in list(words):
        words += append_common_numbers(w)
    print(f"[+] After appending common numbers: {len(words)} items")

    # special chars
    final_words = []
    for w in words:
        final_words += special_chars_variants(w)
    print(f"[+] After applying special characters variants: {len(final_words)} items")

    # leet
    if getattr(profile, "leet_enabled", False):
        leet_words = []
        for w in final_words:
            leet_words += apply_leet(w)
        final_words += leet_words
        print(f"[+] After applying leet transformations: {len(final_words)} items")

    # dedupe and filter
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
    # target name variants
    target_name_variants = _collect_target_variants(profile)
    print(f"[+] Target name variants: {len(target_name_variants)}")

    # important words (including name variants)
    important_words = _collect_important_words(profile, target_name_variants)
    print(f"[+] Important words base: {len(important_words)}")

    # dates
    date_list = _collect_dates(profile)
    print(f"[+] Date variants collected: {len(date_list)}")

    # keep a mutable date_list for downstream processors (they may append)
    date_list = list(date_list)

    # prepare target last name for person processing
    target_last = sanitize_word(profile.name.strip().split()[-1]).lower() if profile.name else ""

    # relations
    processed_relations, relation_words = _process_people(profile.relationships, target_last, target_name_variants, date_list)
    print(f"[+] Relations processed: {len(processed_relations)} — relation words {len(relation_words)}")

    # children
    processed_children, children_words = _process_people(profile.children, target_last, target_name_variants, date_list)
    print(f"[+] Children processed: {len(processed_children)} — children words {len(children_words)}")
    # combos between children (without dates)
    for c1, c2 in itertools.permutations(processed_children, 2):
        for v1 in c1.get("name_vars", []):
            for v2 in c2.get("name_vars", []):
                children_words.append(v1 + v2)

    # pets
    processed_pets, pet_words = _process_pets(profile.pets, target_name_variants, date_list)
    print(f"[+] Pets processed: {len(processed_pets)} — pet words {len(pet_words)}")
    pet_words += combine_pets(processed_pets)

    # include initial target words
    words = []
    words += target_name_variants
    words += important_words
    words += relation_words
    words += children_words
    words += pet_words
    print(f"[+] Accumulated words before combos/transforms: {len(words)}")

    # combos: target <-> important words
    for w in important_words:
        for tn in target_name_variants:
            words.append(tn + w)
            words.append(w + tn)

    # combos: target <-> relations
    for rel in processed_relations:
        for tn in target_name_variants:
            for rv in rel.get("name_vars", []) + rel.get("nickname_vars", []):
                words.append(tn + rv)
                words.append(rv + tn)

    # entity <-> date combos
    all_entities = []
    all_entities += target_name_variants
    for rel in processed_relations:
        all_entities += rel.get("name_vars", []) + rel.get("nickname_vars", [])
    for child in processed_children:
        all_entities += child.get("name_vars", []) + child.get("nickname_vars", [])
    for pet in processed_pets:
        all_entities += pet.get("name_vars", []) + pet.get("nickname_vars", [])
    all_entities += important_words

    words += _combine_entity_date_combos(all_entities, date_list)
    print(f"[+] Added date combos: total words now {len(words)}")

    # apply transformations and filtering
    filtered = _apply_final_transforms(words, profile)
    print(f"[+] Final filtered wordlist size: {len(filtered)}")

    return filtered, len(filtered)


def generate_pinlist(profile, length=4):
    """
    Generate PIN list based on dates in the profile.
        Returns the PIN list and its count.
    """
    from pathlib import Path

    def extract_pins_from_date(d):
        if not d:
            return set()

        day = f"{d.day:02d}"
        month = f"{d.month:02d}"
        year = str(d.year)
        year_short = year[-2:]

        variants = set()
        # basic combos
        variants.update({day + month, month + day, month + year_short, day + year_short})
        variants.update({day + month + year_short, month + day + year_short, day + month + year, month + day + year})
        variants.update({year, year_short})
        return {v for v in variants if v.isdigit()}

    # collect date-based pins
    pins = set()
    if profile.birth:
        pins.update(extract_pins_from_date(profile.birth))
    for d in profile.important_dates:
        pins.update(extract_pins_from_date(d))
    for rel in profile.relationships:
        if rel.get("birth"):
            pins.update(extract_pins_from_date(rel["birth"]))
    for child in profile.children:
        if child.get("birth"):
            pins.update(extract_pins_from_date(child["birth"]))
    for pet in profile.pets:
        if pet.get("birth"):
            pins.update(extract_pins_from_date(pet["birth"]))

    # filter for requested length
    generated = [p for p in sorted(pins) if len(p) == int(length)]

    # T9-generated pins from names/keywords/etc. (old mobile keypad)
    t9_single = set()
    t9_multi = set()

    def add_t9_variants(s):
        if not s:
            return
        from magicguess.utils import sanitize_word
        cleaned = sanitize_word(s)
        if not cleaned:
            return
        single = string_to_t9(cleaned)
        multi = string_to_t9_multi(cleaned)
        if single and len(single) == int(length) and single.isdigit():
            t9_single.add(single)
        if multi and len(multi) == int(length) and multi.isdigit():
            t9_multi.add(multi)

    # collect candidates
    add_t9_variants(profile.name)
    for kw in profile.keywords:
        add_t9_variants(kw)
    for em in profile.emails:
        if em:
            add_t9_variants(em.split("@")[0])
    for rel in profile.relationships:
        add_t9_variants(rel.get("name"))
        add_t9_variants(rel.get("nickname"))
    for child in profile.children:
        add_t9_variants(child.get("name"))
        add_t9_variants(child.get("nickname"))
    for pet in profile.pets:
        add_t9_variants(pet.get("name"))
        add_t9_variants(pet.get("nickname"))

    t9_single_sorted = sorted(t9_single)
    t9_multi_sorted = sorted(t9_multi)

    # Load base Markov PIN file and prioritize generated pins
    base_file = Path(__file__).parent / f"PIN{length}_markov.txt"
    base_list = []
    if base_file.exists():
        try:
            raw = base_file.read_bytes()
            encoding = None
            # detect BOMs
            if raw.startswith(b"\xef\xbb\xbf"):
                encoding = "utf-8-sig"
            elif raw.startswith(b"\xff\xfe"):
                encoding = "utf-16"
            elif raw.startswith(b"\xfe\xff"):
                encoding = "utf-16-be"

            if not encoding:
                try:
                    text = raw.decode("utf-8")
                    encoding = "utf-8"
                except Exception:
                    try:
                        text = raw.decode("utf-16")
                        encoding = "utf-16"
                    except Exception:
                        text = raw.decode("latin-1")
                        encoding = "latin-1"
            else:
                text = raw.decode(encoding)

            base_list = [ln.strip() for ln in text.splitlines() if ln.strip()]
            print(f"[+] Loaded base PIN list from {base_file.name} ({len(base_list)} entries) using encoding {encoding}")
        except Exception as e:
            print(f"[!] Failed to read {base_file.name}: {e}")
            base_list = []
    else:
        print(f"[!] Base PIN file not found: {base_file.name}.")
        print("[!] You can create it yourself to keep the repo small. Example command:")
        print(f"    hashcat -a 3 {'?d'*int(length)} --stdout > {base_file.name}")
        # Ask the user whether to let MagicGuess create the file
        resp = input(f"[?] Do you want MagicGuess to create {base_file.name} now? (y/N): ").strip().lower()
        if resp in ("y", "yes"):
            total = 10 ** int(length)
            # warn for large files
            WARN_LIMIT = 2_000_000
            if total > WARN_LIMIT:
                confirm = input(f"[!] This will create {total:,} lines (large file). Continue? (y/N): ").strip().lower()
                if confirm not in ("y", "yes"):
                    print("[!] Skipping automatic creation. Using generated date-based PINs only.")
                    base_list = []
                else:
                    # create file by streaming
                    print(f"[+] Creating {base_file.name} with {total:,} entries (this may take some time)...")
                    with base_file.open("w", encoding="utf-8") as fh:
                        for i in range(total):
                            fh.write(str(i).zfill(int(length)) + "\n")
                            if i > 0 and i % 1000000 == 0:
                                print(f"  wrote {i:,} lines...")
                    print(f"[+] Created {base_file.name}")
                    # no shuffle option: created file left ordered
                    # load base_list
                    with base_file.open("r", encoding="utf-8") as fh:
                        base_list = [ln.strip() for ln in fh if ln.strip()]
            else:
                # small-ish file: safe to create
                print(f"[+] Creating {base_file.name} with {total:,} entries...")
                with base_file.open("w", encoding="utf-8") as fh:
                    for i in range(total):
                        fh.write(str(i).zfill(int(length)) + "\n")
                print(f"[+] Created {base_file.name}")
                # created file left ordered 
                with base_file.open("r", encoding="utf-8") as fh:
                    base_list = [ln.strip() for ln in fh if ln.strip()]
        else:
            print("[!] Skipping base file creation. Using generated date-based PINs only.")

    # Build final list: 1) date-based generated, 2) T9-generated, 3) remaining base entries
    generated_set = set(generated)
    t9_single_set = set(t9_single_sorted) if 't9_single_sorted' in locals() else set()
    t9_multi_set = set(t9_multi_sorted) if 't9_multi_sorted' in locals() else set()
    final = []
    # 1) add date-based generated (sorted)
    for p in generated:
        final.append(p)
    # 2) add T9-generated pins next
    for p in t9_single_sorted:
        if p not in generated_set:
            final.append(p)
    for p in t9_multi_sorted:
        if p not in generated_set and p not in t9_single_set:
            final.append(p)
    # 2.5) add known/common PIN patterns (in this order: increasing, decreasing, repeated digits, special vertical column for 4-digit)
    def _known_patterns(n):
        n = int(n)
        patterns = []
        # increasing (1..n) if n <= 9, else use 0..9 cycling
        if n <= 9:
            inc = ''.join(str(i) for i in range(1, n+1))
        else:
            inc = ''.join(str(i % 10) for i in range(1, n+1))
        patterns.append(inc)
        # decreasing
        patterns.append(inc[::-1])

        # repeated digits 0..9 (e.g., 0000, 1111 ...)
        for d in range(0, 10):
            patterns.append(str(d) * n)

        # special case: vertical middle column on phone keypad for 4-digit pins
        if n == 4:
            patterns.insert(0, '2580')
            patterns.insert(1, '0852')

        # keep only numeric and correct length
        return [p for p in patterns if p.isdigit() and len(p) == n]

    patterns = _known_patterns(length)
    for p in patterns:
        if p not in generated_set and p not in t9_single_set and p not in t9_multi_set:
            final.append(p)
    # 3) then add from base_list if not present in prior sets
    prior = set(final)
    for p in base_list:
        if not p.isdigit():
            continue
        if len(p) != int(length):
            continue
        if p in prior:
            continue
        final.append(p)

    # ensure uniqueness
    final_unique = []
    seen = set()
    for p in final:
        if p in seen:
            continue
        seen.add(p)
        final_unique.append(p)

    print(f"[+] Generated {len(generated)} date-based PINs; T9(single) {len(t9_single_sorted)}; T9(multi) {len(t9_multi_sorted)}; final PINlist length: {len(final_unique)}")
    return final_unique, len(final_unique)
