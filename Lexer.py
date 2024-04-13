from Tokenizer import *

class Lexer:
    tokens = []

    def __init__(self, tokenizer: "Tokenizer") -> None:
        self.tokenizer = tokenizer

    def generate_tokens(self, file_name):
        self.tokens = []
        with open(file_name, "r") as file:

            for line_number, line in enumerate(file.readlines(), start=1):
                if line.strip() == "":
                    continue

                # Make sure the end statement character is alone
                line = line.replace(";", " ; ")
                line = line.replace("(", " ( ")
                line = line.replace(")", " ) ")
                line = line.replace("{", " { ")
                line = line.replace("}", " } ")
                line = line.replace("=", " = ")
                line = line.replace("= =", " == ")
                line = line.replace(">", " > ")
                line = line.replace("<", " < ")
                line = line.replace("! =", " != ")
                line = line.replace("+", " + ")
                line = line.replace("-", " - ")
                line = line.replace("*", " * ")
                line = line.replace("/", " / ")
                line = line.replace('"', ' " ')

                # Reverse the input
                line_stack = line.strip().split(" ")[::-1]

                while len(line_stack) != 0:
                    # Cleaning the input
                    lexeme = line_stack.pop()
                    lexeme = lexeme.strip()

                    # Ignore empty lines
                    if lexeme == "":
                        continue

                    else:
                        token = self.tokenizer.create_token(lexeme, self)

                        if token.error_msg != None:
                            raise SyntaxError(
                                f"{token.error_msg} at line: {line_number}"
                            )

                        self.tokens.append(token)

        # self.tokens = tokens
        # print(self.get_tokens())
        return self.tokens

    def get_tokens(self):
        return self.tokens
