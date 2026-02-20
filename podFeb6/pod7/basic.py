# TASK: Tokenize input
# TASK: error for input that doesn't have tokens
# TASK: create abstract syntax tree 
# TASK: error for missing tokens in AST
# TASK: calculate expression


from strings_with_arrows import *

###########
#POSITION
###########

class Position:
    def __init__(self, ln, idx, col, userInput, fileName):
        self.ln = ln
        self.idx = idx
        self.col = col
        self.userInput = userInput
        self.fileName = fileName

    def __repr__(self):
        return f'{self.ln}:{self.idx}:{self.col}'

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.col = 0
            self.ln += 1

    def copy(self):
        return Position(self.ln, self.idx, self.col, self.userInput, self.fileName)

###########
#ERROR
###########

class Error:
    def __init__(self, errorName, errorDetails, pos_start, pos_end):
        self.errName = errorName
        self.errorDetails = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end
        print(f'{self.pos_start} is the pos_start')
        print(f'{self.pos_end} is pos_end')

    def __repr__(self):
        errMsg = f'{self.errName}: {self.errorDetails}\n'
        errMsg += f'File {self.pos_start.fileName}, Line {self.pos_start.ln}\n'
        errMsg += string_with_arrows(self.pos_start.userInput, self.pos_start, self.pos_end)
        return errMsg
    
class InvalidCharError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("InvalidCharError", errorDetails, pos_start, pos_end)

class InvalidSyntaxError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("InvalidSyntaxError", errorDetails, pos_start, pos_end)
    

###########
#TOKENS
###########

DIGITS = '0123456789'
DOT = '.'

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_POW = 'POW'

TT_EOF = 'EOF'

class Token:
    def __init__(self, type, pos_start, pos_end = None, value = None):
        self.type = type
        self.value = value 
        self.pos_start = pos_start.copy()
        self.pos_end = pos_start.copy()
        self.pos_end.advance()

        if self.pos_end:
            self.pos_end = self.pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
########
# LEXER - tokenizes input
########

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        # self.index = -1
        self.position = Position(0, -1, -1, userInput, fileName)
        self.currentChar = None
        self.advance()

    def advance(self):
        self.position.advance()
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None
    
    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.position))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.position))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TT_MUL, pos_start=self.position))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(TT_DIV, pos_start=self.position))
                self.advance()
            elif self.currentChar == '^':
                tokens.append(Token(TT_POW, pos_start=self.position))
                self.advance()
            elif self.currentChar == '(':
                print(f'{self.position} in token')
                tokens.append(Token(TT_LPAREN, pos_start=self.position))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.position))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                pos_start = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, InvalidCharError(f"'{currentChar}'", pos_start, self.position)
        tokens.append(Token(TT_EOF, pos_start=self.position))
        return tokens, None
    
    def makeNumberTokens(self):
        numStr = ''
        dotCount = 0
        pos_start = self.position.copy()
        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dotCount == 1:
                    break
                dotCount += 1
            numStr += self.currentChar
            self.advance()
        if dotCount == 1:
            return Token(TT_FLOAT, pos_start=pos_start, pos_end=self.position, value = float(numStr))
        return Token(TT_INT, pos_start=pos_start, pos_end=self.position, value = int(numStr))
    
##########
#PARSERESULT
##########

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

    def register(self, obj):
        if isinstance(obj, ParseResult):
            if obj.error:
                self.error = obj.error
            return obj.node
        return obj
    
    
##########
#NODE
##########

class NumberNode:
    def __init__(self, numberToken):
        self.numberToken = numberToken

    def __repr__(self):
        return f'{self.numberToken}'

class BinaryNode:
    def __init__(self, leftNode, op_token, rightNode):
        self.leftNode = leftNode
        self.op_token = op_token
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.leftNode}, {self.op_token}, {self.rightNode})'

class UnaryNode:
    def __init__(self, op_token, rightNode):
        self.op_token = op_token
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.op_token}, {self.rightNode})'
    

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = -1
        self.currentToken = None
        self.advance()
    
    def advance(self):
        self.index += 1
        self.currentToken = self.tokens[self.index] if self.index < len(self.tokens) else None
    
    def atom(self):
        parseResultObj = ParseResult()
        token = self.currentToken

        if token.type in (TT_INT, TT_FLOAT):
            self.advance()
            return parseResultObj.success(NumberNode(token))
        elif token.type == TT_LPAREN:
            self.advance()
            exprNode = parseResultObj.register(self.expr())
            if parseResultObj.error:
                return parseResultObj
            if self.currentToken.type == TT_RPAREN:
                self.advance()
                return parseResultObj.success(exprNode)
            else:
                #return error
                return parseResultObj.failure(
                    InvalidSyntaxError("required ')' right paran", self.currentToken.pos_start, self.currentToken.pos_end)
                )
        else:
            return parseResultObj.failure(
                InvalidCharError("required number or math symbol or paranExpr", token.pos_start, token.pos_end)
            )

            
    def power(self):
        return self.bin_op(self.atom, (TT_POW,), self.factor)
    
    def factor(self):
        parseResultObj = ParseResult()
        if self.currentToken.type in (TT_PLUS, TT_MINUS):
            op_token = self.currentToken
            self.advance()
            rightNode = parseResultObj.register(self.factor())
            if parseResultObj.error:
                return parseResultObj
            return parseResultObj.success(
                UnaryNode(op_token, rightNode))
        return self.power()
    
    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))
    
    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, funcA, opTokens, funcB = None):
        if funcB == None:
            funcB = funcA
        parseResultObj = ParseResult()
        leftNode = parseResultObj.register(funcA())
        if parseResultObj.error:
            return parseResultObj
        while self.currentToken.type in opTokens:
            op_token = self.currentToken
            self.advance()
            rightNode = parseResultObj.register(funcB())
            if parseResultObj.error:
                return parseResultObj
            leftNode = BinaryNode(leftNode, op_token, rightNode)
        return parseResultObj.success(leftNode)
        
    def parser(self):
        parseResultObj = ParseResult()
        expr = self.expr()
        if self.currentToken.type != TT_EOF and not expr.error:
            return parseResultObj.failure(
                InvalidSyntaxError("Expected a math symbol", self.currentToken.pos_start, self.currentToken.pos_end)
            )
        return expr
    

############
#INTERPRETER
############

class PNumber:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'
    
    def addTo(self, other):
        return PNumber(self.value + other.value)
    
    def subBy(self, other):
        return PNumber(self.value - other.value)
    
    def mulTo(self, other):
        return PNumber(self.value * other.value)
    
    def divBy(self, other):
        return PNumber(self.value / other.value)

class Interpreter:
    def visit_node(self, node):
        self.node = node
        typeOfNode = type(self.node).__name__
        methodName = f'visit_{typeOfNode}'
        method = getattr(self, methodName, self.no_visit_method)
        return method(node)
    
    def visit_UnaryNode(self, node):
        print(f'visit_unary{node}')
        op_token = node.op_token
        self.visit_node(node.rightNode)

    def visit_BinaryNode(self, node):
        print(f'visit_Binary{node}')
        op_token = node.op_token
        leftNode = node.leftNode
        rightNode = node.rightNode
        self.visit_node(leftNode)
        self.visit_node(rightNode)

    def visit_NumberNode(self, node):
        print(f'visit_number{node.numberToken}')

    def no_visit_method(self, node):
        raise Exception(f' there is no visit method for this node: {node}')
    
############
#RUN
############
def run(userInput, fileName):
    lexerInstance = Lexer(userInput, fileName)
    tokens, error =  lexerInstance.makeTokens()
    if error:
        return None, error
    parserInstance = Parser(tokens)
    print(f'tokens: {tokens}')
    ast = parserInstance.parser()

    if ast.error:
        return None, ast.error
    
    interPreter = Interpreter()
    interPreter.visit_node(ast.node)

    return ast.node, ast.error
