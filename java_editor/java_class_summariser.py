from java_lexer import Lexer
from java_regex import JavaRegex, JavaPattern
from java_token import Token


class ClassSummariser:
    COMMA_PATTERN = JavaPattern("VALUE", [Lexer.VALUE_COMMA], [])
    OPEN_BRACE_PATTERN = JavaPattern("VALUE", ["{"], [])
    CLOSE_BRACE_PATTERN = JavaPattern("VALUE", ["}"], [])

    def __init__(self, class_file, target_name):
        self.class_file = class_file
        self.target_name = target_name
        with open(class_file, "r") as f:
            self.class_text = f.read()
            self.class_lines = self.class_text.split("\n")

        self.class_definitions = []
        self.function_definitions = {}
        self.variable_definitions = {}

        self.tokens = []
        self.line_tokens = []
        self.class_code_lines = []
        
        self.lexer = Lexer(None)
        self.initialize_lists()
        
        self.package = ""
        self.privacy = ""
        self.class_type = ""
        self.name = ""
        self.extends = ""
        self.implements = ""
        self.abstract = False

        self.variables = {}
        self.functions = {}

        self.get_class_details()
        self.get_class_members()
    
    def initialize_lists(self):
        for line in self.class_lines:
            tokens = self.lexer.get_tokens(line)
            self.line_tokens.append(tokens)
            self.tokens.extend(tokens)

    def get_class_details(self):
        i = 0
        finding_end = False
        end_index = 0
        for line in self.line_tokens:
            if finding_end:
                if i >= end_index:
                    break
                self.class_code_lines.append(line)
            elif Lexer.PACKAGE_REGEX.is_match(line):
                self.package = "".join([token.value for token in line[1:-1]])
            elif Lexer.CLASS_CREATION_REGEX.is_match(line):
                output = ClassSummariser.parse_class_creation_line(line)
                if output[2] == self.target_name:
                    self.privacy, self.class_type, self.name, self.extends, self.implements, self.abstract = output
                    brace_index = i + len(line) - 1
                    end_index = Lexer.get_closing_bracket(self.tokens, brace_index, "{", "}")
                    finding_end = True

            i += len(line)

    def get_class_members(self):
        within_function = False
        i = 0
        brace_no = 0
        for line in self.class_code_lines:
            if brace_no == 0 and Lexer.ASSIGNMENT_REGEX.is_match(line):
                var_properties = ClassSummariser.parse_variable_creation_line(line)
                self.variables[var_properties[0]] = {"type": var_properties[1], "scope": var_properties[2], "properties": {"final": var_properties[3], "static": var_properties[4], "volatile": var_properties[5]}}
            elif Lexer.FUNCTION_CREATION_REGEX.is_match(line):
                func_properties = ClassSummariser.parse_function_creation_line(line)
                self.functions[func_properties[0]] = {
                    "type": func_properties[1], 
                    "scope": func_properties[2], 
                    "properties": {"final": func_properties[3], "static": func_properties[4], "abstract": func_properties[5]},
                    "args": func_properties[6]
                }
            brace_no += ClassSummariser.OPEN_BRACE_PATTERN.count(line)
            brace_no -= ClassSummariser.CLOSE_BRACE_PATTERN.count(line)

    @staticmethod
    def parse_variable_creation_line(tokens):
        scope = "private"
        final = False
        static = False
        volatile = False
        var_type = ""
        var_name = ""
        get_var_name = False
        for token in tokens:
            if token.value in JavaRegex.VARIABLE_SCOPES:
                scope = token.value
            elif token.value == "static":
                static = True
            elif token.value == "final":
                final = True
            elif token.value == "volatile":
                volatile = True
            elif token.value in JavaRegex.VARIABLE_TYPES or (token.type == Lexer.TYPE_VAR and not get_var_name):
                var_type = token.value
                get_var_name = True
            elif get_var_name:
                var_name = token.value
                get_var_name = False
        return var_name, var_type, scope, final, static, volatile

    @staticmethod
    def parse_function_creation_line(tokens):
        get_name = False
        name = ""
        rtype = ""
        scope = "private"
        static = False
        final = False
        abstract = False
        arg_types = []

        i = 0

        for token in tokens:
            if token.value in JavaRegex.VARIABLE_SCOPES:
                scope = token.value
            elif token.value == "static":
                static = True
            elif token.value == "final":
                final = True
            elif token.value == "abstract":
                abstract = True
            elif token.value in JavaRegex.VARIABLE_TYPES or (token.type == Lexer.TYPE_VAR and not get_name) or token.value == "void":
                get_name = True
                rtype = token.value
            elif get_name:
                name = token.value
                get_name = False
            elif token.value == "(":
                break
            i += 1
        
        closing_index = Lexer.get_closing_bracket(tokens, i)
        for type_token, name_token in ClassSummariser.COMMA_PATTERN.split(tokens[i+1:closing_index]):
            arg_types.append(type_token)
        
        return name, rtype, scope, final, static, abstract, arg_types

    @staticmethod
    def parse_class_creation_line(tokens):
        get_class = False
        class_name = ""
        get_extends = False
        extends = ""
        get_implements = False
        implements = ""
        scope = ""
        class_type = ""
        abstract = False
        for token in tokens:
            if token.value in JavaRegex.VARIABLE_SCOPES:
                scope = token.value
            elif token.value == "abstract":
                abstract = True
            elif token.value in ["class", "interface", "enum"]:
                get_class = True
                class_type = token.value
            elif token.value == "extends":
                get_extends = True
            elif token.value == "implements":
                get_implements = True
            elif get_class:
                class_name = token.value
                get_class = False
            elif get_extends:
                extends = token.value
                get_extends = False
            elif get_implements:
                implements = token.value
                get_implements = False
        if scope == "":
            scope = "private"
        return scope, class_type, class_name, extends, implements, abstract


if __name__ == "__main__":
    summariser = ClassSummariser("cool_minecraft_mod/custom_java/MetalDetectorItem.java", "MetalDetectorItem")
    print(summariser.package)
    print(summariser.privacy, summariser.class_type, summariser.name, summariser.extends, summariser.implements, summariser.abstract)
    print(summariser.variables)