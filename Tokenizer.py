import re
from Lexer import Lexer

class Tokenizer:

    def __init__(self, token_path) -> None:
        self.bnf = {}
        self.casting = {}
        self.token = {}

        using_function = None

        with open(token_path) as file:  
            for data_input in file.readlines():
                data_input = data_input.strip()
                if data_input == "BNF":
                    using_function = self.collect_bnf
                elif data_input == "CASTING":
                    using_function = self.collect_casting
                elif data_input == "TOKEN":
                    using_function = self.collect_token
                else:
                    using_function(data_input)
 

    def create_token(self, text, lexer: exec):
        return Token(text, self, lexer)
    
    def collect_bnf(self, data_input):
        data_input = data_input.split("->")
        self.bnf[data_input[0].strip()] = re.compile(data_input[1].strip())
    
    def collect_casting(self, data_input):
        data_input = data_input.split("->")
        casting = data_input[0].split(",")
        self.casting[(casting[0].strip(), casting[1].strip())] = data_input[1].strip()
    
    def collect_token(self, data_input):
        data_input = data_input.split("->")
        self.token[data_input[0].strip()] = re.compile(data_input[1].strip())
        

class Token:
    def __init__(self, text, tokenizer: Tokenizer, lexer: Lexer) -> None:
        self.error_msg = None
        self.text = text
        self.token_name = None

        # Token names
        QOUTE = "<QOUTE>"
        IDENORCHAR = "<IDENTIFIER>|<CHARACTERS>"

        for token, pattern in tokenizer.token.items():
            if re.fullmatch(pattern, text):
                self.token_name = token

                if len(lexer.get_tokens()) != 0:
                    # Get the last element from the list. Will return token in form (<OPEN_BRACKET>:{)
                    last_element = str(lexer.get_tokens()[len(lexer.get_tokens())-1])

                    # Extracted content within angle brackets including the brackets
                    type_pattern = r'<[^>]*>'
                    prev_type = Token.extract(type_pattern, last_element)

                    # Extracted content between ":" and ")"
                    valuePattern = r':([^)]*)\)$'
                    prev_value = Token.extract(valuePattern, last_element)

                    # Checks last token to see if it should be added to or made a string literal
                    Token.updatePrev(QOUTE, prev_type, QOUTE, self, prev_value, lexer)
                    Token.updatePrev(QOUTE, prev_type, IDENORCHAR, self, prev_value, lexer)     
                    Token.updatePrev(IDENORCHAR, prev_type, QOUTE, self, prev_value, lexer)
                    Token.updatePrev(IDENORCHAR, prev_type, IDENORCHAR, self, prev_value, lexer)
                return
            
        self.error_msg = f"'{text}' is not recognized"

    def __str__(self) -> str:
        return f"({self.token_name}:{self.text})"

    def __repr__(self) -> str:
        return self.__str__()
    
    def extract(pattern, last_token):
        matches = re.findall(pattern, last_token)
        return matches[0] if matches else None
    
    def __hash__(self):
        return hash((self.text, self.token_name))
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.token_name == other
        
        elif isinstance(other, Token):
            return (self.text, self.token_name) == (other.text, other.token_name)

    def __ne__(self, other):
        return not(self == other)
    # if quote == prevtype and quote == currType
    # if quote == prevtype and ind|chars == currType
    # if ind|chars == prevtype and quote == currType
    # if ind|chars == prevtype and ind|chars == currType
    def updatePrev(prev_check, prev_type, curr_check, curr_type, prev_value, lexer: Lexer):
        STRING_LITERAL = r"\"[a-zA-Z0-9 ]*\"|\"\""
        IDENORCHAR = "<IDENTIFIER>|<CHARACTERS>"
        STRING_TOKEN_NAME = "<STRING_LITERAL>"
        CHARACTERS = "<CHARACTERS>"
        
        if re.fullmatch(prev_check,prev_type) and re.fullmatch(curr_check, str(curr_type.token_name)):
            # Get the correct spacing
            space = " " if CHARACTERS == prev_type and re.fullmatch(IDENORCHAR, str(curr_type.token_name)) else ""
            # Update value and token type
            if re.fullmatch(STRING_LITERAL, curr_type.text):
                curr_type.token_name = STRING_TOKEN_NAME
            else:
                curr_type.text = prev_value + space + curr_type.text
                curr_type.token_name = CHARACTERS
                # Remove token just read as it was added to prev token 
                del lexer.get_tokens()[len(lexer.get_tokens())-1]

            
    

