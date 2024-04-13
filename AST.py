from Tokenizer import *


class AST:

    def __init__(self, tokenizer: Tokenizer) -> None:
        self.tokenizer = tokenizer
        self.root: Binary_Operation_Node = Block_Node(self)

    def traverse(self):
        for node in self.root.children:
            print(node.operator)
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


class Node:
    def __init__(self, ast: AST, token: Token, isleaf: bool) -> None:
        self.token: Token = token
        self.ast = ast
        self.isleaf = isleaf
        self.data_type = token.token_name if token != None else None

    def generate_assembly(self):
        raise NotImplementedError("The node")

    def __str__(self) -> str:
        return self.token.__str__()

    def __repr__(self) -> str:
        return self.__str__()


class Constant_Node(Node):
    def __init__(self, ast, token: Token) -> None:
        super().__init__(ast, token, True)

    def generate_assembly(self):
        return f"{self.token}"


class Identifier_Node(Node):
    def __init__(self, ast, token: Token, data_type: str, heap_index) -> None:
        super().__init__(ast, token, True)
        self.data_type = data_type
        self.heap_index = heap_index

    def __str__(self) -> str:
        return self.token.__str__()

    def __repr__(self) -> str:
        return self.__str__()

    def generate_assembly(self):
        # return f"{self.heap_index}"
        return ""


class Function_Node(Node):
    pass


class Variable_Node(Node):
    def __init__(self, ast, variable_name, node) -> None:
        super().__init__(ast, None, False)
        self.variable_name = variable_name
        self.data_type = node.left.data_type
        self.child = node.right

    def generate_assembly(self):
        return "do stuff"

    def __str__(self) -> str:
        return self.variable_name.__str__()

    def __repr__(self) -> str:
        return self.__str__()


class Binary_Operation_Node(Node):
    def __init__(self, ast, operator, left, right) -> None:
        super().__init__(ast, None, False)
        self.operator = operator

        self.left: Node = left
        self.right: Node = right
     
        if (self.ast.tokenizer.casting.get((self.left.data_type, self.right.data_type)) == None):
            raise SyntaxError(f"Cannot {operator} {self.right.data_type} with {self.left.data_type}")

        self.data_type = self.ast.tokenizer.casting[(self.left.data_type, self.right.data_type)]

    def generate_assembly(self):
        operation = []
        if self.operator == "=":
            operation = f""

        if self.operator == "+":
            operation = ["add", "$t2", "$t0", "$t1"]

        if self.operator == "-":
            operation = ["sub", "$t2", "$t0", "$t1"]

        if self.operator == "*":
            operation = ["mul", "$t2", "$t0", "$t1"]

        if self.operator == "/":
            operation = ["div", "$t2", "$t0", "$t1"]

        is_left_leaf = self.left.isleaf and not isinstance(self.left, Identifier_Node)
        is_right_leaf = self.right.isleaf and not isinstance(self.right, Identifier_Node)

        statement = ""
        if is_left_leaf and is_right_leaf:
            statement += f"li $t0, {self.left.generate_assembly()}\n"
            statement += f"li $t1, {self.right.generate_assembly()}\n"
            statement += f"{operation[0]}, {", ".join(operation[1:])}\n"
            statement += f"add $s0, $0, $t2\n"

        elif is_left_leaf:
            statement += self.right.generate_assembly()
            statement += f"li $t0, {self.left.generate_assembly()}\n"
            operation[3] = "$s0"
            statement += f"{operation[0]}, {", ".join(operation[1:])}\n"
            statement += f"add $s0, $0, $t2\n"

        elif is_right_leaf:
            statement += self.left.generate_assembly()
            statement += f"li $t1, {self.right.generate_assembly()}\n"
            operation[2] = "$s0"
            statement += f"{operation[0]}, {", ".join(operation[1:])}\n"
            statement += f"add $s0, $0, $t2\n"

        else:
            statement += f"{self.left.generate_assembly()}"
            statement += f"{self.right.generate_assembly()}"

        return statement

    def __str__(self) -> str:
        if self.operator == "=":
            return f"{self.left.data_type.__str__():<7} {self.left.__str__():<3} {self.operator} {self.right.data_type} {self.right}"
        return f"({self.left} {self.operator} {self.right})"

    def __repr__(self) -> str:
        return self.__str__()


class Block_Node(Node):
    def __init__(self, ast) -> None:
        super().__init__(ast, None, False)
        self.children = []

    def generate_assembly(self):
        results = ""
        for node in self.children:
            results += node.generate_assembly()
            results += "li $v0, 1\n"
            results += "move $a0, $t2\n"
            results += "syscall\n"

        return results

    def __str__(self) -> str:
        res = ""
        for node in self.children:
            res += f"{node}\n"
        return res

    def __repr__(self) -> str:
        return self.__str__()
