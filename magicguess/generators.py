# generators.py

from magicguess.utils import sanitize_word, dedupe, normalize_string
from datetime import datetime
import itertools

SPECIAL_CHARS = ['!', '@', '#', '$', '%', '&', '*']
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
    """Aplica substituições simples, apenas 1 letra por vez, sem explosão."""
    variants = set([word])

    for idx, ch in enumerate(word.lower()):
        if ch in LEET_MAP:
            for sub in LEET_MAP[ch]:
                new_word = list(word)
                new_word[idx] = sub
                variants.add("".join(new_word))

    return list(variants)


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
    """
    Gera variações:
      - toggles individuais de cada parte (first, middle(s), last)
      - combinações compostas SOMENTE se incluírem o primeiro nome ou a inicial do primeiro
      - inclui variante initial+middle+last (ex: MDinisBregieira)
      - evita combos que sejam apenas middle+last (para não explodir)
    """
    parts_raw = [p for p in full_name.strip().split() if p]
    parts = [sanitize_word(p) for p in parts_raw]
    if not parts:
        return []

    # toggles por parte (lista de listas)
    toggles_per_part = [toggle_case(p) for p in parts]

    # 1) Variantes simples: todos os toggles individuais (first, middle(s), last)
    simple_names = list(itertools.chain.from_iterable(toggles_per_part))

    # 2) Combinações compostas — só combos que incluam a parte 0 (primeiro)
    combined = []
    # produto cartesiano de toggles (gera combos com todas as partes)
    for combo in itertools.product(*toggles_per_part):
        # combo é uma tupla com uma variante por parte, ex ("marcelo","dinis","bregieira")
        # incluímos apenas se a combinação **mantém o primeiro** (sempre vai manter, pois produto inclui todas),
        # mas podemos querer filtrar combos que não comecem com o primeiro (caso venham reordenados) — aqui mantemos a ordem original.
        # O critério é: incluir combos que contenham o primeiro (sempre true) -> mas queremos também permitir combos parciais
        # com apenas first+last (ignorando middle), e full first+middle+last.
        # Vamos construir explicitamente as variantes desejadas:
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

    # 7) Aplica o LEET mode
    if profile.leet_enabled:
        leet_words = []
        for w in final_words:
            leet_words += apply_leet(w)
        final_words += leet_words


    # 8) Dedup e filtrar palavras inválidas
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

    return filtered, len(filtered)

# -------------------------
# TODO: PIN list
# -------------------------
def generate_pinlist(profile):
    return []  # placeholder
