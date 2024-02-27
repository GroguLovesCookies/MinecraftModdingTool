from java_token import Token


class JavaRegex:
    VARIABLE_IDENTIFIERS = ["static", "final", "volatile"]
    VARIABLE_SCOPES = ["public", "private", "protected"]
    VARIABLE_TYPES = ["boolean", "byte", "char", "double", "float", "int", "long", "short"]

    keys = {
        "\i": VARIABLE_IDENTIFIERS,
        "\s": VARIABLE_SCOPES,
        "\t": VARIABLE_TYPES
    }

    def __init__(self, pattern):
        self.pattern = pattern

    @classmethod
    def fromString(cls, string):
        splits = string.split(">")
        pattern = {}
        for split in splits:
            temp = {}
            compounds = split.split("|")
            total = compounds[:-2] if len(compounds) > 1 else compounds
            for compound in total:
                arg_splits = compound.split(",")
                match_type = arg_splits[0]
                match_value = arg_splits[1]
                match_min = arg_splits[2]
                match_max = arg_splits[3]
                match_values = []
                negative_values = []
                for part in match_value.split("/"):
                    if part in JavaRegex.keys:
                        match_values.extend(JavaRegex.keys[part])
                    else:
                        if part.startswith("!"):
                            negative_values.append(part[1:])
                        else:
                            match_values.append(part)
                
                temp[JavaPattern(match_type, match_values, negative_values)] = JavaQuantifier(int(match_min), int(match_max))
            if len(temp) > 1:
                pattern[JavaPattern("OR", temp, [])] = JavaQuantifier(int(compounds[-2]), int(compounds[-1]))
            else:
                pattern[list(temp.keys())[0]] = temp[list(temp.keys())[0]]
        return cls(pattern)

    def is_match(self, tokens):
        i = 0
        for pattern, quantifier in self.pattern.items():
            j = 0
            if i == len(tokens):
                return False
            token = tokens[i]
            while pattern.matches(token) and i < len(tokens):
                j += 1
                i += 1
                if i < len(tokens):
                    token = tokens[i]
                else:
                    break
            validation = quantifier.validate(j)
            if validation == -1:
                return False
            while validation == 1:
                i -= 1
                j -= 1
                validation = quantifier.validate(j)
        return True

            


class JavaPattern:
    def __init__(self, pattern_type, values, negative_values):
        self.type = pattern_type
        self.values = values
        self.negative_values = negative_values

    def matches(self, token):
        if self.type == "AND":
            is_match = True
            for pattern in self.values:
                is_match = is_match and pattern.matches(token)
            return is_match
        elif self.type == "OR":
            is_match = False
            for pattern in self.values:
                is_match = is_match or pattern.matches(token)
            return is_match
        elif self.type == "TYPE":
            return (token.type in self.values or len(self.values) == 0) and token.type not in self.negative_values
        elif self.type == "VALUE":
            return (token.value in self.values or len(self.values) == 0) and token.value not in self.negative_values
        elif self.type == "PSTYPE":
            return (token.pseudotype in self.values or len(self.values) == 0) and token.pseudotype not in self.negative_values


class JavaQuantifier:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value):
        if self.min_value > value:
            return -1
        elif self.max_value < value:
            return 1
        else:
            return 0

