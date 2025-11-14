# lógica principal: gerar guesses a partir do MasterGuess

class MasterGuess:
    def __init__(self, name, birth, relationships=None, children=None, pets=None,
                 important_dates=None, keywords=None):

        self.name = name
        self.birth = birth

        self.relationships = relationships or []
        self.children = children or []
        self.pets = pets or []
        self.important_dates = important_dates or []
        self.keywords = keywords or []

        self.wordlist = []
        self.pinlist = []
