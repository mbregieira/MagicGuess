# Wordlist && PINlist Generator

An **profile-based wordlist generator** designed for **digital forensics** and **penetration testing**.
The tool focuses on **high-value, realistic passwords** while actively preventing unnecessary combinatorial explosion.

---

## Key Features

### Profile-Driven Generation
The wordlist is generated from a structured target profile, including:
- **Target (primary person)**
- **Relations** (partner, spouse, etc.)
- **Children**
- **Pets**
- **Emails**
- **Important words**
- **Important dates**

Each category can generate passwords **independently** or in **controlled combinations**.

---

### Important Dates (centralized logic)
**Important dates** are automatically applied to:
- Target
- Relations
- Children
- Pets
- Important words

Sources include:
- Dates of birth
- Manually entered dates via CLI
- Relevant events

Dates are normalized into multiple formats, such as:
- `DDMMYYYY`
- `DDMMYY`
- `MMYYYY`
- `YYYY`

These are reused across the generator to avoid duplication and explosion.

---

### Intelligent Name Handling
- Case toggling is applied **per individual word**
- Compound names are built by **joining existing toggled variants**, not by re-toggling
- Middle names are handled contextually to avoid redundant combinations
- Same-surname relations are sanitized to prevent outputs like:
    SurnameSurname
- This guarantees valid outputs such as:
NameSurname
nameSurname
NameSURNAME

---

### Relations, Children, and Pets (standalone & combined)
Relations, children, and pets can generate passwords:
- **On their own**
- **Combined with target data**
- **Combined between themselves**

Examples:
Sarah1988*
Diana120519
Nadine110978
LaraJohn

Passwords made **only of dates** are never generated.

---

### Email-Based Word Extraction
The local part of emails (before `@`) is parsed to extract:
- Base word
- Numeric suffixes
- Date and number combinations

Example:

marcelo90@gmail.com

→ marcelo
→ marcelo90
→ 90
→ marcelo1990
→ 1990marcelo

---

### Leetspeak (Optional)
Leet transformations:
- Are applied **only if explicitly enabled**
- Run **after all base generation**
- Never applied blindly to avoid explosion

Example:

Marcelo → M4rcelo


---

### Special Characters (Controlled)
Special characters are added in a **strictly limited way**:
- At the beginning
- At the end
- At both beginning and end

Multiple special characters in sequence are not allowed.

---

### Explosion Prevention
Several safeguards are in place:
- Duplicate elimination at all stages
- Centralized date reuse
- Same-surname relation sanitization
- No numeric-only or date-only passwords
- Leet applied last, if enabled

---

## Generation Flow (High Level)

1. Input normalization and sanitization  
2. Base word extraction  
3. Case toggling per word  
4. Centralized important date generation  
5. Controlled cross-combinations  
6. Optional leet transformation  
7. Final deduplication  
8. Simple counter reports total combinations generated  

---

Purpose

This tool is designed to generate wordlists that are ideal for:

1. DFIR professionals
2. Law enforcement investigations
3. Penetration testers
4. Red teams
5. Password policy audits

License
Educational and professional use is permitted only in legal and authorized contexts.