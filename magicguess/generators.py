# generators.py

# generators.py
import re
from datetime import date
from .transforms import clean, normalize_string, split_email_parts

# Helpers for birth/date variants (keep compact)
def birthdate_variants(birthdate: date):
    if not isinstance(birthdate, date):
        return []
    y = str(birthdate.year)
    yy = y[-2:]
    dd = f"{birthdate.day:02d}"
    mm = f"{birthdate.month:02d}"
    return [dd+mm+y, dd+mm+yy, y, yy, dd+mm]

# Extract name variants with priority: first, last, fullname (no spaces)
def name_variants(name: str):
    if not name:
        return []
    s = normalize_string(name)
    parts = s.split()
    out = []
    if len(parts) == 1:
        out.append(parts[0])
    else:
        out.append(parts[0])                 # first
        out.append(parts[-1])                # last
        out.append("".join(parts))           # full concat
    # initials (low priority)
    if len(parts) >= 2:
        out.append("".join([p[0] for p in parts]))
    return list(dict.fromkeys([clean(x) for x in out if x]))

# Email local splitting (kept simple)
def email_local_chunks(email_local: str):
    # split alpha/digits runs
    if not email_local:
        return []
    chunks = re.findall(r"[A-Za-z]+|\d+", email_local)
    return [clean(c) for c in chunks if c]

# MAIN extraction: returns dict with 'high','medium','low' lists
def extract_profile_variables(profile):
    HIGH = []
    MEDIUM = []
    LOW = []

    # Name (target)
    if profile.name:
        nv = name_variants(profile.name)
        # prefer first and last; ensure ordering: first, last, full
        if nv:
            # nv already in that order
            HIGH.extend(nv[:3])

    # Target birth
    if profile.birth:
        HIGH.extend(birthdate_variants(profile.birth))

    # Relationships (partner/confidant)
    for r in profile.relationships:
        if getattr(r, "first_name", None):
            HIGH.append(r.first_name)
        if getattr(r, "last_name", None):
            MEDIUM.append(r.last_name)
        if getattr(r, "nickname", None):
            MEDIUM.append(r.nickname)
        if getattr(r, "birthdate", None):
            MEDIUM.extend(birthdate_variants(r.birthdate))

    # Children (high for child names, child dates high)
    for c in profile.children:
        if getattr(c, "first_name", None):
            HIGH.append(c.first_name)
        if getattr(c, "nickname", None):
            MEDIUM.append(c.nickname)
        if getattr(c, "birthdate", None):
            HIGH.extend(birthdate_variants(c.birthdate))

    # Pets (names high)
    for p in profile.pets:
        if getattr(p, "name", None):
            HIGH.append(p.name)
        if getattr(p, "birthdate", None):
            MEDIUM.extend(birthdate_variants(p.birthdate))

    # Important dates (medium)
    for d in profile.important_dates:
        MEDIUM.extend(birthdate_variants(d))

    # Keywords (medium)
    for k in profile.keywords:
        MEDIUM.append(k)

    # Emails (low priority: local and domain base)
    for e in profile.emails:
        if getattr(e, "local", None):
            LOW.extend(email_local_chunks(e.local))
            LOW.append(e.local)
        if getattr(e, "domain", None):
            parts = e.domain.split(".")
            if parts:
                LOW.append(parts[0])  # main domain e.g., hotmail, gmail

    # Clean + dedupe each priority preserving rough order
    def clean_and_unique(seq):
        out = []
        seen = set()
        for item in seq:
            item = clean(item)
            if not item:
                continue
            if item not in seen:
                out.append(item)
                seen.add(item)
        return out

    return {
        "high": clean_and_unique(HIGH),
        "medium": clean_and_unique(MEDIUM),
        "low": clean_and_unique(LOW)
    }

# Convenience: produce ordered list with priority weighting (high first)
def generate_base_words(profile, include_low=False):
    vars = extract_profile_variables(profile)
    base = []
    base.extend(vars["high"])
    base.extend(vars["medium"])
    if include_low:
        base.extend(vars["low"])
    # final dedupe while preserving order
    out = []
    s = set()
    for w in base:
        if w and w not in s:
            out.append(w)
            s.add(w)
    return out
