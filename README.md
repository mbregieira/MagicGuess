# MagicGuess - Wordlist & PINlist Generator

A **profile-based wordlist and PINlist generator** designed for **digital forensics** and **penetration testing**.  
The tool focuses on **high-value, realistic passwords and PINs** commonly encountered in real-world engagements.

---

## Key Features

### Profile-Driven Generation
The wordlist is generated from a structured target profile, including:
- **Target** (primary person)
- **Relations** (partner, spouse, etc.)
- **Children**
- **Pets**
- **Emails**
- **Important keywords**
- **Important dates**

Each category can generate passwords **independently** or in **controlled combinations**.

---

### Important Dates (Centralized Logic)

**Important dates** are automatically applied to:
- Target
- Relations
- Children
- Pets
- Important keywords

**Date sources include:**
- Dates of birth
- Manually entered dates via CLI
- Relevant events (anniversaries, etc.)

**Date formats generated:**
- `DDMMYYYY` / `MMDDYYYY` (full year)
- `DDMMYY` / `MMDDYY` (short year)
- `DDMM` / `MMDD` (no year)
- `YYYY` / `YY` (year only)

**Priority ordering:**
- European format (`DDMM`) prioritized first
- American format (`MMDD`) second
- Other combinations follow

These are reused across the generator to avoid duplication and explosion.

---

### Name Handling

- Case toggling is applied **per individual word**
- Compound names are built by **joining existing toggled variants**, not by re-toggling
- Middle names are handled contextually to avoid redundant combinations
- Same-surname relations are sanitized to prevent outputs like `SurnameSurname`

**Valid outputs include:**
```
NameSurname
nameSurname
NameSURNAME
NSurname
nSurname
```

---

### Relations, Children, and Pets (Standalone & Combined)

Relations, children, and pets can generate passwords:
- **On their own**
- **Combined with target data**
- **Combined between themselves**

**Examples:**
```
Sarah1988*
Diana120519
Nadine110978
LaraJohn
MarcelloMia
```

---

### Email-Based Extraction

The local part of emails (before `@`) is parsed to extract:
- Base word
- Numeric sequences (for PINs)
- Date and number combinations

**Example:**
```
mbregieira846884@hotmail.com
→ mbregieira
→ mbregieira846884
→ 846884 (extracted as PIN)
→ mbregieira93
→ 93mbregieira
```

---

###  PINlist Generation

**PIN generation with priority ordering:**

1. ** Date-based PINs** (highest priority)
   - Birth dates (target, relations, children, pets)
   - Important dates
   - Multiple formats: `DDMM`, `DDMMYY`, `DDMMYYYY`, etc.
   - European format (`DDMM`) prioritized over American (`MMDD`)

2. ** Numeric sequences from emails/keywords**
   - Extracted from emails: `user846884@domain.com` → `846884`
   - Extracted from keywords with numbers
   - All possible substrings of desired length

3. ** T9 keypad conversions**
   - Single-press: `MARCELO` → `6272356`
   - Multi-press: `MARCELO` → `6262777222333555666`

4. ** Known common patterns**
   - Sequential: `1234`, `123456`
   - Reversed: `4321`, `654321`
   - Repeated: `0000`, `1111`, `9999`
   - Keypad patterns: `2580`, `0852` (vertical swipes)

5. ** Base markov list** (if available)
   - Optionally generated using hashcat
   - Example: `hashcat -a 3 ?d?d?d?d --stdout > PIN4_markov.txt`

**Supported PIN lengths:** 4, 6, or custom

---

### Leetspeak (Optional)

Leet transformations:
- Applied **only if explicitly enabled**
- Run **after all base generation**
- Never applied blindly to avoid explosion
- Substitutes one character at a time

**Example:**
```
Marcelo → M4rcelo, Marc3lo, Marce1o
```

To prevent explosion, you can do the same with rules with Hashcat, try it out!

---

### Special Characters (Controlled)

Special characters (`!@#$%&*"`) are added in a **limited way**:
- At the beginning: `!Marcelo`
- At the end: `Marcelo!`
- At both ends: `!Marcelo!`

---

### Explosion Prevention

Several safeguards are in place:
- Duplicate elimination at all stages
- Centralized date reuse
- Same-surname relation sanitization
- No numeric-only passwords
- No date-only passwords
- Minimum password length filtering (6+ characters)
- Leet applied last, if enabled
- Controlled cross-combinations

---

## Generation Flow (High Level)

### Wordlist Generation:
1. Input normalization and sanitization
2. Base word extraction (names, keywords, emails)
3. Case toggling per word
4. Centralized important date generation
5. Controlled cross-combinations (target ↔ relations/pets)
6. Common number appending (`1`, `123`, `1234`, etc.)
7. Special character variants
8. Optional leet transformation
9. Final deduplication and filtering
10. Progress reporting with counters

### PINlist Generation:
1. Date extraction and formatting with priority
2. Numeric sequence extraction from emails/keywords
3. T9 keypad conversion (single and multi-press)
4. Known pattern generation
5. Optional base list loading/creation
6. Priority-ordered final list assembly
7. Deduplication maintaining order

---

## Purpose

This tool is designed to generate wordlists and PINlists that are ideal for:
1. **DFIR professionals** (Digital Forensics)
2. **Law enforcement investigations**
3. **Penetration testers**
4. **Red teams**
5. **Password policy audits**
6. **Security awareness training**

---

## Usage

```bash
python mg.py

# Follow the prompts to:
# 1. Enter target information
# 2. Add relations, children, pets
# 3. Specify important dates and keywords
# 4. Choose wordlist, PINlist, or both
```

---

## Output

- **Wordlist:** `AwesomeWordlist.txt` (or custom filename)
- **PINlist:** `AwesomePINlist.txt` (or custom filename)
- Both files include generation statistics and priority ordering

---

## License & Legal Notice

**Educational and professional use is permitted only in legal and authorized contexts.**

- Use only on systems you own or have explicit written authorization to test
- Intended for legitimate security research and forensic analysis
- Unauthorized access to computer systems is illegal
- The authors are not responsible for misuse of this tool

**By using this tool, you agree to use it responsibly and ethically.**

---

## Contributing

Contributions are welcome! 

---

**Remember:** With great power comes great responsibility. Use MagicGuess ethically and legally.