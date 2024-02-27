class Token:
    def __init__(self, tok_type, tok_value, tok_pseudotype=""):
        self.type = tok_type
        self.value = tok_value
        self.pseudotype = tok_pseudotype
        self.args = []

    def __repr__(self):
        return f"{self.type}:{self.value}"
