from Tokenizer import *


class AST:

    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer
        self.root: Block_Node = None

    def traverse(self):
        for node in self.root.children:
            if isinstance(node, Binary_Operation_Node) and node.operator == "=":
                variable = node.left
                value = node.right
                print(variable)
                print(value)
        return
    
    def __str__(self) -> str:
        return self.root.__str__()

    def __repr__(self) -> str:
        return self.__str__()

    def generate_python(self):
        return "if __name__ == '__main__':\n" + self.root.generate_python(0 ,isRoot=True)

class Node:
    def __init__(self, ast: AST, token: Token, isleaf: bool) -> None:
        self.token: Token = token
        self.ast = ast
        self.isleaf = isleaf
        self.data_type = token.token_name if type(token) == Token  else None

    def generate_python(self):
        raise NotImplementedError("The node")

    def __str__(self) -> str:
        return self.token.__str__()

    def __repr__(self) -> str:
        return self.__str__()


class Constant_Node(Node):
    def __init__(self, ast: AST, token: Token) -> None:
        super().__init__(ast, token, True)

    def generate_python(self, tab_index):
        # Gets rid of f at the end of floats 
        return f"{self.token.text[:-1] if self.token.text.endswith('f') else self.token.text}"
    

class Identifier_Node(Node):
    def __init__(self, ast: AST, token: Token, data_type: str, heap_index) -> None:
        super().__init__(ast, token, True)
        self.data_type = data_type
        self.heap_index = heap_index

    def __str__(self) -> str:
        return self.token.__str__()

    def __repr__(self) -> str:
        return self.__str__()

    def generate_python(self, tab_index:int):
        return self.token.text

class Function_Node(Node):
    # pass in a list of tokens rather than a token
    def __init__(self, ast: AST, function_name:str, parameters) -> str:
        super().__init__(ast, None, False)
        self.parameters = parameters
        self.function_name = function_name
        
    def __str__(self) -> str:
        return "function"

    def __repr__(self) -> str:
        return self.__str__()
    
    def generate_python(self, tab_index:int):
        # join via commas when arrays
        # return f"{'\t'*tab_index}{self.function_name}({self.parameters.text})"    
        return "{}{}({})\n".format('\t' * tab_index, self.function_name, self.parameters.text)   

class Variable_Node(Node):
    def __init__(self, ast: AST, variable_token: Token, node) -> None:
        super().__init__(ast, variable_token, False)
        self.data_type = node.left.data_type
        self.child = node.right

    def generate_python(self, tab_index:int):
        return self.token.text

    def __str__(self) -> str:
        return self.token.text

    def __repr__(self) -> str:
        return self.__str__()


class Binary_Operation_Node(Node):
    def __init__(self, ast: AST, operator:str, left:Node, right:Node) -> None:
        super().__init__(ast, None, False)
        self.operator = operator

        self.left: Node = left
        self.right: Node = right
     
        if (self.ast.tokenizer.casting.get((self.left.data_type, self.right.data_type)) == None):
            raise SyntaxError(f"Cannot {operator} {self.right.data_type} with {self.left.data_type}")

        self.data_type = self.ast.tokenizer.casting[(self.left.data_type, self.right.data_type)]

    def generate_python(self, tab_index:int, newLine: bool = True):
        # return f"{'\t' * tab_index}{self.left.generate_python(0)} {self.operator} {self.right.generate_python(0)}{'\n' if newLine else ''}"
        return "{}{} {} {}{}".format('\t' * tab_index, self.left.generate_python(0), self.operator, self.right.generate_python(0), '\n' if newLine else '')

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"

    def __repr__(self) -> str:
        return self.__str__()


class Block_Node(Node):
    def __init__(self, ast: AST, operation: str, parameter_node: Node = None) -> None:
        super().__init__(ast, None, False)
        self.children = []
        self.operation = operation
        self.parameter : Binary_Operation_Node = parameter_node

    def generate_python(self, tab_index: int, isRoot=False):
        # results = f"{'\t' * tab_index}{self.operation.lower()} "
        # results += f"({self.parameter.generate_python(0, newLine=False)})" if self.parameter != None else ""

        if self.parameter is not None:
            results = "{}{}({})".format('\t' * tab_index, self.operation.lower(), self.parameter.generate_python(0, newLine=False))
        elif self.operation == "ELSE":
            results = "\n{}{}".format('\t' * tab_index, self.operation.lower())
        else:
            results = "{}{}".format('\t' * tab_index, self.operation.lower())

        results += ":\n" if not isRoot else "\n"
        
        for node in self.children:
            results += node.generate_python(tab_index + 1)
        return results

    def __str__(self) -> str:
        res = f"{self.operation}:\n"
        for node in self.children:
            res += f"{node}\n"
        return res.strip() + "\nCLOSE"

    def __repr__(self) -> str:
        return self.__str__()
