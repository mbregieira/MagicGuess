# core.py

# Core data classes for MagicGuess

from datetime import date

# ==============================
# CORE DATA CLASSES
# ==============================

class Relationship:
    def __init__(self, name: str, birth: date = None, nickname: str = None):
        self.name = name
        self.birth = birth
        self.nickname = nickname


class Child:
    def __init__(self, name: str, birth: date = None, nickname: str = None):
        self.name = name
        self.birth = birth
        self.nickname = nickname


class Pet:
    def __init__(self, name: str, birth: date = None):
        self.name = name
        self.birth = birth


class Email:
    def __init__(self, address: str):
        self.address = address


class MasterGuess:
    def __init__(
        self,
        name: str,
        birth: date = None,
        relationships: list = None,
        children: list = None,
        pets: list = None,
        important_dates: list = None,
        keywords: list = None,
        emails: list = None,
        leet_enabled: bool = False
    ):
        self.name = name
        self.birth = birth
        self.relationships = relationships or []
        self.children = children or []
        self.pets = pets or []
        self.important_dates = important_dates or []
        self.keywords = keywords or []
        self.emails = emails or []
        self.leet_enabled = leet_enabled

        self.wordlist = []
        self.pinlist = []
