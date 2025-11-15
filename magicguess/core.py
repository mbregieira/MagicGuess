# Criar o objeto principal que vai ser a base para as combinações e posteriores transformações

from datetime import date
from typing import List, Optional
from .transforms import normalize_string, clean

class Relationship:
    def __init__(self, first_name: str, last_name: Optional[str]=None,
                 nickname: Optional[str]=None, birthdate: Optional[date]=None):
        self.first_name = normalize_string(first_name) if first_name else None
        self.last_name = normalize_string(last_name) if last_name else None
        self.nickname = normalize_string(nickname) if nickname else None
        self.birthdate = birthdate

class Child:
    def __init__(self, first_name: str, last_name: Optional[str]=None,
                 nickname: Optional[str]=None, birthdate: Optional[date]=None):
        self.first_name = normalize_string(first_name) if first_name else None
        self.last_name = normalize_string(last_name) if last_name else None
        self.nickname = normalize_string(nickname) if nickname else None
        self.birthdate = birthdate

class Pet:
    def __init__(self, name: str, birthdate: Optional[date]=None):
        self.name = normalize_string(name) if name else None
        self.birthdate = birthdate

class Email:
    def __init__(self, address: str):
        self.raw = address or ""
        parts = self.raw.split("@", 1) if "@" in self.raw else [self.raw, None]
        self.local = clean(parts[0]) if parts[0] else None
        self.domain = parts[1].lower() if parts[1] else None

class MasterGuess:
    """
    Central profile object. Use named fields (first/middle/last) or provide a full name.
    """
    def __init__(self,
                 name: Optional[str],
                 birth: Optional[date],
                 relationships: Optional[List[Relationship]] = None,
                 children: Optional[List[Child]] = None,
                 pets: Optional[List[Pet]] = None,
                 important_dates: Optional[List[date]] = None,
                 keywords: Optional[List[str]] = None,
                 emails: Optional[List[Email]] = None,
                 leet_enabled: bool = False):
        # keep original name string but also split later in generators
        self.name = normalize_string(name) if name else None
        self.birth = birth

        self.relationships = relationships or []
        self.children = children or []
        self.pets = pets or []

        self.important_dates = important_dates or []
        self.keywords = [normalize_string(k) for k in (keywords or [])]
        self.emails = emails or []

        self.leet_enabled = leet_enabled

        # outputs
        self.wordlist = []
        self.pinlist = []
