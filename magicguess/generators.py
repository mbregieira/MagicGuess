# generators.py

# generators.py

from magicguess.utils import sanitize_word, dedupe, normalize_string
from datetime import datetime
import itertools

SPECIAL_CHARS = ['!', '@', '#', '$', '%', '&', '*']
COMMON_NUMBERS = ["1", "12", "123", "1234", "69", "7", "17", "123456"]
MIN_LENGTH = 6

# -------------------------
# Toggle case das palavras individuais
# -------------------------
def toggle_case(word):
    return list(dedupe([
        word.lower(),
        word.capitalize(),
        word.upper() if len(word) > 1 else word.upper()
    ]))

# -------------------------
# Nome variantes
# -------------------------
def name_variants(full_name: str):
    """Gera variações de nomes individuais e compostos corretos."""
    parts = [sanitize_word(p) for p in full_name.strip().split() if p]
    individual_variants = [toggle_case(p) for p in parts]

    # Flatten para nomes simples
    simple_names = list(itertools.chain.from_iterable(individual_variants))

    # Combinar palavras individuais em nomes compostos
    combined_variants = []
    for combo in itertools.product(*individual_variants):
        combined_variants.append(''.join(combo))

    return dedupe(simple_names + combined_variants)

# -------------------------
# Datas variantes
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
                variants.add(f"{month}{day}{year}")  # invertido

    variants.add(year_full)
    variants.add(year_short)

    return list(dedupe(variants))

# -------------------------
# Caracteres especiais
# -------------------------
def special_chars_variants(word):
    variants = [word]
    for c in SPECIAL_CHARS:
        variants.append(c + word)
        variants.append(word + c)
        variants.append(c + word + c)
    return variants

# -------------------------
# Números comuns
# -------------------------
def append_common_numbers(word):
    return [word + n for n in COMMON_NUMBERS]

# -------------------------
# Geração da wordlist
# -------------------------
def generate_wordlist(profile):
    words = []

    # 1) Nomes
    if profile.name:
        words += name_variants(profile.name)

    # 2) Palavras importantes
    for kw in profile.keywords:
        if kw:
            words += toggle_case(sanitize_word(normalize_string(kw)))

    words = dedupe(words)

    # 3) Datas importantes
    date_list = []
    if profile.birth:
        date_list += date_variants(profile.birth)
    for d in profile.important_dates:
        date_list += date_variants(d)
    date_list = dedupe(date_list)

    # 4) Combina palavras importantes com datas
    important_words = words.copy()
    combined_words = []
    for w in important_words:
        for dtv in date_list:
            combined_words.append(w + dtv)

    words += combined_words
    words += date_list  # manter datas isoladas

    # 5) Aplicar números comuns apenas às palavras importantes
    numbered_words = []
    for w in important_words:
        numbered_words += append_common_numbers(w)
    words += numbered_words

    # 6) Aplicar caracteres especiais (inicio/fim/inicio+fim)
    final_words = []
    for w in words:
        final_words += special_chars_variants(w)

    # 7) Dedup e filtrar palavras inválidas
    final_words = dedupe(final_words)
    filtered = []
    for w in final_words:
        if len(w) < MIN_LENGTH:
            continue
        # descartar se só números ou só especiais
        if w.isdigit():
            continue
        if all(c in SPECIAL_CHARS for c in w):
            continue
        filtered.append(w)

    return filtered

# -------------------------
# TODO: PIN list
# -------------------------
def generate_pinlist(profile):
    return []  # placeholder
