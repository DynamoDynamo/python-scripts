
#TASK: Build a lexer to tokonize userinput
#TASK: Build parser

from strings_with_arrows import *

################
#TOKENS
################
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV' 
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_EOF = 'EOF'
DIGITS = '0123456789'
DOT = '.'

class Tokens:
    def __init__(self, tokenType, tokenValue = None, pos_start = None, pos_end = None):
        self.type = tokenType
        self.value = tokenValue
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
################
#POSITION - position of a word, line wise, col wise, index wise
################

class Position:
    def __init__(self, line, col, index, fileName, userInput):
        self.ln = line
        self.idx = index
        self.col = col
        self.userInput = userInput
        self.fileName = fileName

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.ln += 1
            self.col = 0

        return self
    
    def copy(self): #Return current position object
        return Position(self.ln, self.col, self.idx, self.fileName, self.userInput)
    
################
#ERROR
################

class Error:
    def __init__(self, errorName, errDetails, pos_start, pos_end):
        self.errorName = errorName
        self.details = errDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg = f'{self.errorName}: {self.details}\n'
        errMsg += f'FILE {self.pos_start.fileName}, LINE {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.userInput, self.pos_start, self.pos_end)
        return errMsg
    
class IllegalCharError(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("IllegalCharError", errDetails, pos_start, pos_end)

class InvalidSyntaxError(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidSyntaxError", errDetails, pos_start, pos_end)

    
################
#LEXER
################

class Lexer:
    def __init__(self, fileName, userInput):
        self.fileName = fileName
        self.userInput = userInput
        self.currentChar = None
        self.position = Position(0, -1, -1, fileName, userInput)
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Tokens(TT_PLUS, pos_start=self.position))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Tokens(TT_MINUS, pos_start=self.position))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Tokens(TT_MUL, pos_start=self.position))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Tokens(TT_DIV, pos_start=self.position))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Tokens(TT_LPAREN, pos_start=self.position))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Tokens(TT_RPAREN, pos_start=self.position))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                currentChar = self.currentChar
                currentPos = self.position.copy()
                self.advance()
                return None, IllegalCharError("'" + currentChar + "'", currentPos, self.position)
        tokens.append(Tokens(TT_EOF, pos_start=self.position))
        return tokens, None
    
    def makeNumberTokens(self):
        num_str = ''
        dot_count = 0
        pos_start = self.position.copy()

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()
        
        if dot_count == 1:
            return Tokens(TT_FLOAT, float(num_str), pos_start=pos_start, pos_end=self.position)
        else:
            return Tokens(TT_INT, int(num_str), pos_start, self.position)
    
################
#NODES
################

class NumberNode:
    def __init__(self, token):
        self.tok = token

    def __repr__(self):
        return f'{self.tok}'
    
class BinaryOpNode:
    def __init__(self, leftNode, opToken, rightNode):
        self.left_node = leftNode
        self.op_tok = opToken
        self.right_node = rightNode

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'
    

################
#PARSERESULT
################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self

################
#PARSER
################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    
    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(
                InvalidSyntaxError("Expected + - * /", self.current_tok.pos_start, self.current_tok.pos_end)
            )
        return res
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if(tok.type in (TT_INT, TT_FLOAT)):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        return res.failure(InvalidSyntaxError("expected int or float", tok.pos_start, tok.pos_end))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS)) 

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinaryOpNode(left, op_tok, right)
        return res.success(left)


################
#RUN
################
def run(fileName, userInput):
    lexerInstance = Lexer(fileName, userInput)
    tokens, error = lexerInstance.makeTokens()
    if error:
        return None, error

    #Generate Abstract Syntax Tree
    parser = Parser(tokens)
    res = parser.parse()

    return res.node, res.error