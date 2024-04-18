from Tokenizer import * 
from Lexer import *
from Parser import *
import os

if __name__ == '__main__':
    token_path = "./mojoRegex.type"
    tokenizer = Tokenizer(token_path)
    lexer = Lexer(tokenizer)
    lexer.generate_tokens("ex1.mojo")
    parser = Parser(lexer.get_tokens(), tokenizer)
    ast = parser.generate_AST()
    print(ast.generate_python())

