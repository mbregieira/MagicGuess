# transforms.py
import itertools
import unicodedata
import datetime

# Basic cleaning & normalization
def normalize_string(s: str) -> str:
    if not s:
        return ""
    normalized = unicodedata.normalize("NFKD", s)
    return "".join(c for c in normalized if not unicodedata.combining(c))

def clean(s: str) -> str:
    if not s:
        return ""
    s = normalize_string(s)
    s = s.strip()
    s = s.replace(" ", "")
    return s

# Email helpers (kept minimal here)
def split_email_parts(email: str):
    if "@" not in email:
        return [email, None]
    user, domain = email.split("@", 1)
    return [user, domain]

# Leet with strict cap: max 2 subs (total) irrespective of length (configurable)
LEET_MAP = {
    "a": ["4", "@"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["5", "$"],
    "t": ["7"],
}

def apply_leet_limited(word: str, max_subs=2):
    # positions where substitution possible
    positions = [(i, LEET_MAP[c]) for i, c in enumerate(word.lower()) if c in LEET_MAP]
    if not positions:
        yield word
        return
    max_subs = min(max_subs, len(positions))
    # limit r to 1..max_subs (but be conservative)
    for r in range(1, max_subs+1):
        for subset in itertools.combinations(positions, r):
            replacement_options = [pos[1] for pos in subset]
            # take only the first replacement option per char to limit explosion?
            # We'll still iterate product but max_subs small keeps result small.
            for combo in itertools.product(*replacement_options):
                new = list(word)
                for (pos, _), rep in zip(subset, combo):
                    new[pos] = rep
                yield "".join(new)
    yield word

# Case variants: original, first-upper, last-upper, first+last upper
def apply_case_variants(word: str):
    if not word:
        return []
    w = word.lower()
    out = [w]
    if len(w) >= 1:
        out.append(w[0].upper() + w[1:])
        out.append(w[:-1] + w[-1].upper())
    if len(w) >= 2:
        out.append(w[0].upper() + w[1:-1] + w[-1].upper())
    # return unique preserving order
    seen = set()
    res = []
    for x in out:
        if x not in seen:
            res.append(x)
            seen.add(x)
    return res

# separators small set
SEPARATORS = ["", "_", ".", "-"]

def add_separators(word: str):
    for s in SEPARATORS:
        yield f"{word}{s}"

# numbers and years limited lists
COMMON_SUFFIXES = ["1", "12", "123", "1234", "01", "69", "7"]
def add_numbers(word):
    for n in COMMON_SUFFIXES:
        yield f"{word}{n}"

def add_years(word):
    current = datetime.datetime.now().year
    for y in (current, current-1, current-2):
        yield f"{word}{y}"

# special chars limited: only 1-char prefix/suffix and some 2-char combos
SPECIALS = ['!', '"', '#', '$', '%', '&', '*']
def add_specials_final(password: str, max_prefix=1, max_suffix=1):
    # original
    yield password
    # 1-char prefix/suffix
    for c in SPECIALS:
        yield f"{c}{password}"
        yield f"{password}{c}"
        yield f"{c}{password}{c}"
    # a small set of 2-char combos (not full cartesian) - pick most common pairs
    two_combos = ['!#', '!$', '#$','*&']
    for p in two_combos:
        yield f"{p}{password}"
        yield f"{password}{p}"

# MASTER pipeline with options
def apply_transformations(words, leet_enabled=False, include_low=False,
                          max_leet_subs=2, enable_numbers=True, enable_years=True,
                          enable_specials=True):
    """
    Controlled pipeline:
      - accepts 'leet_enabled' flag
      - transformations applied more aggressively to HIGH, less to MEDIUM, minimal to LOW
    The combinators will call this with appropriately sliced lists.
    """
    transformed = set()

    for w in words:
        base = clean(w)
        if not base:
            continue

        # case variants (list)
        cases = apply_case_variants(base)

        for c in cases:
            # leet layer (generator) or just pass-through
            if leet_enabled:
                leet_iter = apply_leet_limited(c, max_subs=max_leet_subs)
            else:
                leet_iter = [c]

            for lv in leet_iter:
                # separators
                for sv in add_separators(lv):
                    # add original variant
                    transformed.add(sv)
                    # numbers
                    if enable_numbers:
                        for nv in add_numbers(sv):
                            transformed.add(nv)
                    # years
                    if enable_years:
                        for yv in add_years(sv):
                            transformed.add(yv)
                    # specials applied last (controlled)
                    if enable_specials:
                        for sp in add_specials_final(sv):
                            transformed.add(sp)

    return list(transformed)
