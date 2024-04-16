from Tokenizer import *
import re
from AST import *

class Parser:

    def __init__(self, tokens: list[Token], tokenizer: "Tokenizer") -> None:
        

        # Remove all the invalid tokens
        self.tokens: list[Token] = tokens

        self.tokenizer = tokenizer

        # Keeps track of the current token
        self.current_token_index = -1
        self.current_heap_index = 0
        self.current_token = self.advance()
        self.ast = AST(tokenizer)
        self.symbol_table = {}

    # Moves on to the next token in list
    def advance(self):
        
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
            return self.current_token
        return None
    
    # Moves back to the previous token in list
    def retreat(self):
        
        self.current_token_index -= 1
        if self.current_token_index >= 0:
            self.current_token = self.tokens[self.current_token_index]
            return self.current_token
        return None
    
    def peek(self, amount):
        next_index = self.current_token_index + 1
        return self.tokens[next_index:next_index+amount]
    
    # Generator
    def generate_AST(self) -> AST:
        # Reset token index
        self.current_token_index = -1
        self.current_token = self.advance()
        self.symbol_table.clear()

        self.ast.root = self.block("STARTER")
        return self.ast

    # block -> begin {statement}* end
    def block(self, operation="Unnamed"):
        
        if self.current_token.token_name != "<OPEN_BRACKET>":
            raise SyntaxError(f"Expected {'{'} but got {self.current_token.text}")

        block = Block_Node(self.ast, operation)

        self.advance()
        
        while self.current_token.token_name != "<CLOSE_BRACKET>":
            
            # raise check if shits out of bounds the advance func()
            if self.current_token.token_name == "<OPEN_BRACKET>":
                block.children.append(self.block())
            else:
                block.children.append(self.statement())
   

        self.advance()
        return block

    # statement -> (assign|if|function|for|while)
    def statement(self) -> Binary_Operation_Node:
        
        if re.fullmatch(self.tokenizer.bnf["<type>"], self.current_token.token_name):
            return self.assign()
        elif self.current_token.token_name == "<IF>":
            if (self.boolean_expression()):
                return self.block("IF")
        elif self.current_token.token_name == "<WHILE>":
            if (self.boolean_expression()):
                return self.block("WHILE")
        else:
            self.advance()

    # boolean_expression -> expr == expr
    def boolean_expression(self) -> Binary_Operation_Node:
        self.advance()
        if self.current_token.token_name == "<OPEN_PARENTHESIS>":
            self.advance()
            self.advance()

            # print(re.fullmatch(self.peek(1)[0], "="))
            if (self.current_token.text == "=" and re.fullmatch(self.peek(1)[0].text, "=")):
                self.current_token.text =  self.current_token.text + self.peek(1)[0].text
                self.current_token.token_name = "<equality>"
                del self.tokens[self.current_token_index + 1]            

            self.retreat()
            node = self.binary_operation(self.factor, self.factor, ("<equality>"), once=True)

            if (self.current_token.token_name)=="<CLOSE_PARENTHESIS>":
                self.advance()
                return True
        
    def extract(pattern, last_token):
        matches = re.findall(pattern, last_token)
        return matches[0] if matches else None
    
    # assign -> id = expr;
    def assign(self) -> Binary_Operation_Node:
        data_type = self.current_token.token_name

        self.advance()
       
        variable_token = self.current_token
        
        node = self.binary_operation(self.id, self.expr, ("<EQUAL>"), func_left_args=[data_type], once=True)

        variable_node = Variable_Node(self.ast, variable_token, node)

        self.symbol_table[variable_token] = [data_type, variable_node]
    
        if self.current_token.token_name != "<STATEMENT_TERMINATOR>":
            raise SyntaxError("Expected ';'")
        
        self.advance()
        return node
    
    # expr -> term { (+|-) term}*
    def expr(self) -> Binary_Operation_Node:
        return self.binary_operation(self.term, self.term, ("<PLUS>, <MINUS>"))

    def bin_expr(self) -> Binary_Operation_Node:
        return self.boolean_expression(self.factor(), self.factor, (("<EQUAL>")))

    # term -> factor { (*|/) factor}*
    def term(self) -> Binary_Operation_Node:
        return self.binary_operation(self.factor, self.factor, ("<MULTIPLY>, <DIVISION>"))
    
    # factor -> id|int|dec
    def factor(self) -> Node:
        token = self.current_token
        if re.match(self.tokenizer.bnf["<literal>"], token.token_name):
            self.advance()
            return Constant_Node(self.ast, token)
        elif token.token_name == "<IDENTIFIER>":
            
            if (self.symbol_table.get(token) == None):
                raise SyntaxError(f"Unknown symbol: {token.text}")
            
            self.advance()
            return self.symbol_table[token][1]


    # id -> id 
    def id(self, data_type) -> Identifier_Node:
        token = self.current_token
        if token.token_name == "<IDENTIFIER>":
            self.advance()
            node = Identifier_Node(self.ast, token, data_type, self.current_heap_index)
            self.current_heap_index += 4
            return node
        # Throw exception!

    # 
    def binary_operation(self, function_left, function_right, operators: tuple[Token], func_left_args=[], func_right_args=[], once=False) -> Binary_Operation_Node:
        # Calculate left part of tree
        left: Node = function_left(*func_left_args)
        
        # Used only for ensuring 1 iteration
        flag = True

        
        # If the current token is an operation passed in
        # Process the right side then make a new node in the tree
        while self.current_token.token_name in operators and flag:
            operator = self.current_token
            self.advance()
      
            right: Binary_Operation_Node = function_right(*func_right_args)

            # A new "central" node
            left = Binary_Operation_Node(self.ast, operator.text, left, right)

            if once:
                flag = False
      
        # Return the node back up
        return left
    
    def print_symbol_table(self):
     
        for (symbol, variable_data) in self.symbol_table.items():
            print(f"{symbol.__str__():<10} |{variable_data[0]:<10} |{variable_data[1].child.__str__()}")