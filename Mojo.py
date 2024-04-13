from Tokenizer import * 
from Lexer import *
from Parser import *
import os
token_path = "./mojoRegex.type"
tokenizer = Tokenizer(token_path)
lexer = Lexer(tokenizer)
lexer.generate_tokens("ex1.mojo")
parser = Parser(lexer.get_tokens(), tokenizer)
print(parser.generate_AST())