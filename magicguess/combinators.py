# combinators.py
from .generators import extract_profile_variables, generate_base_words
from .transforms import apply_transformations
from .utils import dedupe

# generate_wordlist uses priority groups and conservative transforms
def generate_wordlist(profile):
    """
    Build a prioritized wordlist:
      - Apply stronger transforms to HIGH
      - Medium transforms to MEDIUM (less specials / leet)
      - Optionally include LOW with minimal transforms (no leet, limited specials)
    """
    # get variables
    vars = extract_profile_variables(profile)

    # Options derived from profile
    leet_flag = bool(getattr(profile, "leet_enabled", False))

    final = []

    # 1) HIGH priority: full transforms (leet optional, specials on)
    high = vars["high"]
    if high:
        high_trans = apply_transformations(high,
                                           leet_enabled=leet_flag,
                                           include_low=False,
                                           max_leet_subs=2,
                                           enable_numbers=True,
                                           enable_years=True,
                                           enable_specials=True)
        final.extend(high_trans)

    # 2) MEDIUM priority: fewer specials, maybe no leet or limited
    medium = vars["medium"]
    if medium:
        med_trans = apply_transformations(medium,
                                          leet_enabled=False,    # safer by default
                                          include_low=False,
                                          max_leet_subs=1,
                                          enable_numbers=True,
                                          enable_years=False,     # fewer years
                                          enable_specials=False)  # no heavy specials
        final.extend(med_trans)

    # 3) LOW priority: minimal transforms, only base and small suffixes
    low = vars["low"]
    if low:
        low_trans = apply_transformations(low,
                                          leet_enabled=False,
                                          include_low=True,
                                          max_leet_subs=0,
                                          enable_numbers=False,
                                          enable_years=False,
                                          enable_specials=False)
        final.extend(low_trans)

    # dedupe and keep order
    final = dedupe(final)

    # optionally ensure base names appear first: prepend high base words
    # we'll also add the raw high variables at top for priority
    ordered = []
    for w in high:
        if w not in ordered:
            ordered.append(w)
    for w in final:
        if w not in ordered:
            ordered.append(w)

    return ordered
