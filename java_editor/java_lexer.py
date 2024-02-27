from java_token import Token
from java_regex import JavaRegex


class Lexer:
    TYPE_OPERATOR = "OPERATOR"
    TYPE_INT = "INT"
    TYPE_FLOAT = "FLOAT"
    TYPE_STR = "STR"
    TYPE_DOUBLE = "DOUBLE"
    TYPE_BRACKET = "BRACKET"
    TYPE_VAR = "VAR"
    TYPE_ASSIGNMENT = "ASSIGNMENT"
    TYPE_KW = "KEYWORD"
    TYPE_FUNC = "FUNC"
    TYPE_DUMMY = "DUMMY"

    VALUE_PLUS = "PLUS"
    VALUE_MINUS = "MINUS"
    VALUE_MUL = "TIMES"
    VALUE_DIV = "DIV"
    VALUE_EQUALS = "EQ"
    VALUE_LESS = "LE"
    VALUE_GREATER = "GR"
    VALUE_LESS_EQUALS = "LE"
    VALUE_GREATER_EQUALS = "GRE"
    VALUE_NOT_EQUALS = "NEQ"
    VALUE_AND = "AND"
    VALUE_OR = "OR"
    VALUE_NOT = "NOT"
    VALUE_INCREMENT = "INC"
    VALUE_DECREMENT = "DEC"
    VALUE_INC_1 = "INC1"
    VALUE_DEC_1 = "DEC1"
    VALUE_PAREN = "PAREN"
    VALUE_SQUARE_BRACKET = "SQR"
    VALUE_CURLY_BRACKET = "CURL"
    VALUE_ACCESS = "ACC"
    VALUE_EOS = "EOS"

    PSEUDOTYPE_ASSIGN = "ASSIGN"
    PSEUDOTYPE_REFERENCE = "REFERENCE"
    PSEUDOTYPE_ACCESS = "ACCESS"
    PSEUDOTYPE_OPENING = "OPENING"
    PSEUDOTYPE_CLOSING = "CLOSING"

    STYPE_ASSIGNMENT = "ASSIGN"
    STYPE_EXPRESSION = "EXP"

    OP_CHARS = ["+", "-", "*", "/", "=", "<", ">", "!", "&", "|"]
    KEYWORDS = [
        "abstract", "assert", "boolean",
        "break", "byte", "case", "catch",
        "char", "class", "continue", "default",
        "do", "double", "else", "enum",
        "extends", "final", "finally", "float",
        "for", "if", "implements", "import",
        "instanceof", "int", "interface", "long",
        "native", "new", "package", "private",
        "protected", "public", "return",
        "short", "static", "super", "switch",
        "synchronized", "this", "throw",
        "throws", "transient", "try", "void",
        "volatile", "while", "true", "false",
        "null"
    ]

    ASSIGNMENT_REGEX = JavaRegex.fromString("VALUE,\s,0,1>VALUE,\i,0,1000000000>VALUE,\t,1,1|TYPE,VAR,0,1|1|1>TYPE,VAR,1,1>TYPE,EOS/ASSIGNMENT,1,1")
    CLASS_CREATION_REGEX = JavaRegex.fromString("VALUE,\s,0,1>VALUE,class/enum/interface,1,1>TYPE,VAR,1,1>VALUE,extends,0,1>TYPE,VAR,0,1>VALUE,implements,0,1>TYPE,VAR,0,1>VALUE,{,1,1")
    FUNCTION_CREATION_REGEX = JavaRegex.fromString("VALUE,\s,0,1>VALUE,\i/abstract,0,100000000000>VALUE,\t/void,1,1>TYPE,VAR,1,1>VALUE,(,1,1")
    def __init__(self, document):
        self.document = document

    def get_tokens(self, text):
        tokens = []
        i = 0
        op_text = ""
        num_text = ""
        multiplier = 1
        dot_count = 0
        in_string = ""
        cur_string = ""
        cur_var = ""
        while i < len(text):
            char = text[i]
            if in_string != "":
                if char == in_string:
                    in_string = ""
                    i += 1
                    tokens.append(Token(Lexer.TYPE_STR, cur_string))
                    cur_string = ""
                    continue
                cur_string += char
                i += 1
                continue

            while char in Lexer.OP_CHARS:
                op_text += char
                i += 1
                if i == len(text):
                    break
                char = text[i]
                continue

            if op_text != "":
                if op_text == "+":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_PLUS))
                elif op_text == "-":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_MINUS))
                elif op_text == "*":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_MUL))
                elif op_text == "/":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_DIV))
                elif op_text == "==":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_EQUALS))
                elif op_text == "<":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_LESS))
                elif op_text == ">":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_GREATER))
                elif op_text == "<=":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_LESS_EQUALS))
                elif op_text == ">=":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_GREATER_EQUALS))
                elif op_text == "!=":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_NOT_EQUALS))
                elif op_text == "!":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_NOT))
                elif op_text == "&&":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_AND))
                elif op_text == "||":
                    tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_OR))
                elif op_text == "+=":
                    tokens.append(Token(Lexer.TYPE_ASSIGNMENT, Lexer.VALUE_PLUS))
                elif op_text == "-=":
                    tokens.append(Token(Lexer.TYPE_ASSIGNMENT, Lexer.VALUE_MINUS))
                elif op_text == "*=":
                    tokens.append(Token(Lexer.TYPE_ASSIGNMENT, Lexer.VALUE_MUL))
                elif op_text == "/=":
                    tokens.append(Token(Lexer.TYPE_ASSIGNMENT, Lexer.VALUE_DIV))
                elif op_text == "++":
                    tokens.append(Token(Lexer.TYPE_ASSIGNMENT, Lexer.VALUE_INC_1))
                elif op_text == "--":
                    tokens.append(Token(Lexer.TYPE_ASSIGNMENT, Lexer.VALUE_DEC_1))
                elif op_text == "=":
                    tokens.append(Token(Lexer.TYPE_ASSIGNMENT, Lexer.VALUE_EQUALS))
                elif op_text == "//":
                    return tokens
                op_text = ""
                continue

            while char.isnumeric() or char == "." or (char == "f" and num_text != ""):
                num_text += char
                i += 1
                if char == ".":
                    dot_count += 1
                if i == len(text):
                    break
                char = text[i]
                continue
            
            if num_text != "":
                if True not in [str(j) in num_text for j in range(10)]:
                    num_text = ""
                    dot_count = 0
                    continue
                if dot_count > 1:
                    num_text = ""
                    dot_count = 0
                    continue
                if dot_count == 1 and not num_text.endswith("f"):
                    tokens.append(Token(Lexer.TYPE_DOUBLE, float(num_text)))
                elif num_text.endswith("f"):
                    tokens.append(Token(Lexer.TYPE_FLOAT, float(num_text[:-1])))
                else:
                    tokens.append(Token(Lexer.TYPE_INT, int(num_text)))
                num_text = ""
                dot_count = 0
                continue
            
            if char in ["(", ")", "[", "]", "{", "}"]:
                tokens.append(Token(Lexer.TYPE_BRACKET, char))

            if char == ";":
                tokens.append(Token(Lexer.VALUE_EOS, Lexer.VALUE_EOS))

            if char == "\"" or char == "\'":
                in_string = char
            
            if char == ".":
                tokens.append(Token(Lexer.TYPE_OPERATOR, Lexer.VALUE_ACCESS))
            if char == "~":
                tokens.append(Token(Lexer.TYPE_DUMMY, Lexer.TYPE_DUMMY))
            
            while i < len(text) and (char.isalnum() or char == "_"):
                cur_var += char
                i += 1
                if i < len(text):
                    char = text[i]
            if cur_var != "":
                if cur_var in Lexer.KEYWORDS:
                    tokens.append(Token(Lexer.TYPE_KW, cur_var))
                else:
                    tokens.append(Token(Lexer.TYPE_VAR, cur_var))
                cur_var = ""
                continue
            i += 1
        if cur_var != "":
                if cur_var in Lexer.KEYWORDS:
                    tokens.append(Token(Lexer.TYPE_KW, cur_var))
                else:
                    tokens.append(Token(Lexer.TYPE_VAR, cur_var))
        return tokens


if __name__ == "__main__":
    lexer = Lexer(None)
    with open("cool_minecraft_mod/custom_java/MetalDetectorItem.java", "r") as f:
        for line in f.readlines():
            line = line.expandtabs(4).strip()
            tokens = lexer.get_tokens(line)
            if Lexer.CLASS_CREATION_REGEX.is_match(tokens):
                print(line)
