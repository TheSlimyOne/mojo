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
    def advance(self, num = 1):
        self.current_token_index += num
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
            return self.current_token
        self.current_token = None
        return None
    
    # Moves back to the previous token in list
    def retreat(self, num = 1):
        self.current_token_index -= num
        if self.current_token_index >= 0:
            self.current_token = self.tokens[self.current_token_index]
            return self.current_token
        self.current_token = None
        return None
    
    def peek(self, amount:int):
        next_index = self.current_token_index + 1
        return self.tokens[next_index:next_index+amount]
    
    def isInbounds(self):
        return self.current_token_index < len(self.tokens) and self.current_heap_index >= 0
    
    # Generator
    def generate_AST(self) -> AST:
        # Reset token index
        self.current_token_index = -1
        self.current_token = self.advance()
        self.symbol_table.clear()

        self.ast.root = self.block()
        return self.ast

    # block -> begin {statement}* end
    def block(self, operation=""):        
        if self.current_token.token_name != "<OPEN_BRACKET>":
            raise SyntaxError(f"Expected \"{'{'}\" but got \"{self.current_token.text}\"")

        block = Block_Node(self.ast, operation)
        self.advance()
        
        while self.current_token != None and self.current_token.token_name != "<CLOSE_BRACKET>":
            # raise check if shifts out of bounds the advance func()
            if self.current_token.token_name == "<OPEN_BRACKET>":
                block.children.append(self.block())
            elif self.current_token.token_name == "<PRINT>":
                block.children.append(self.print_statement())
            else:
                block.children.append(self.statement())
        
        # Check for close bracket
        if self.current_token == None:
            raise SyntaxError(f"Expected \"{'}'}\"")
        
        self.advance()
        return block

    # statement -> (assign|if|function|for|while)
    def statement(self) -> Binary_Operation_Node:
        parameter_node = None

        if re.fullmatch(self.tokenizer.bnf["<type>"], self.current_token.token_name):
            return self.assign()
        
        elif self.current_token.token_name == "<PRINT>":
            return self.print_statement()
        
        elif self.current_token.token_name in self.tokenizer.block_statement.keys():
            block_name = self.current_token.token_name
            formatted_name = block_name.replace("<", "").replace(">","")
            block_data = self.tokenizer.block_statement[block_name]
            
            if (block_data[0]):
                parameter_node = self.boolean_expression()
                if (parameter_node != None):
                    block_node = self.block(formatted_name)
                    block_node.parameter = parameter_node
                    return block_node
                else:
                    raise SyntaxError(f"{formatted_name} statement parameters are not defined")
            else:
                self.advance()
                return self.block("ELSE")

    # boolean_expression -> expr == expr
    def boolean_expression(self) -> Binary_Operation_Node:
        self.advance()
        if self.current_token.token_name == "<OPEN_PARENTHESIS>":
            self.advance(2)
        else:
            raise SyntaxError("Expected (")

        if (self.current_token.text == "=" and re.fullmatch(self.peek(1)[0].text, "=")):
            self.current_token.text = self.current_token.text + self.peek(1)[0].text
            self.current_token.token_name = "<equality>"
            del self.tokens[self.current_token_index + 1]            

        self.retreat()
        node = self.binary_operation(self.factor, self.factor, ("<equality>"), once=True)

        if (self.current_token.token_name)=="<CLOSE_PARENTHESIS>":
            self.advance()
            return node
        else:
            raise SyntaxError("Expected )")
    
    # print -> print ("");
    def print_statement(self) -> Function_Node:
        node = self.function_operation(self.current_token.text)
        self.advance()
        return node

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
    def id(self, data_type:str) -> Identifier_Node:
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
    
    # Allows you to make function node 
    # Should update to include multiple parameters
    def function_operation(self, function_name:str) -> Function_Node:
        function_val = self.peek(3)

        open_par = function_val[0]
        parameters = function_val[1]
        close_par = function_val[2]

        func: Function_Node = Function_Node(self.ast, function_name, parameters) 
    
        allowed_param = "<STRING_LITERAL>"

        # Check for format ("");
        if open_par.token_name == "<OPEN_PARENTHESIS>" and parameters.token_name == allowed_param and close_par.token_name == "<CLOSE_PARENTHESIS>":
            self.advance(4)

            if self.current_token.token_name != "<STATEMENT_TERMINATOR>":
                raise SyntaxError("Expected ';'")
        # Will return function type (<PRINT>)
        return func
        
    
    def print_symbol_table(self):
        for (symbol, variable_data) in self.symbol_table.items():
            print(f"{symbol.__str__():<10} |{variable_data[0]:<10} |{variable_data[1].child.__str__()}")

    def merge_token(self, new_token_name:str):
        self.current_token.text += self.peek(1)[0].text
        self.current_token.token_name = new_token_name
        del self.tokens[self.current_token_index + 1]