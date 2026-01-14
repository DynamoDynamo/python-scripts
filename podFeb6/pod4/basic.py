from strings_with_arrows import *


# TASK: tokenize userInput
# TASK: give syntax to tokens and arrange them to nodes


###########
#TOKENS
###########


TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_EOF = "EOF"
DIGITS = "0123456789"
DOT = "."

class Tokens:
    def __init__(self, type, value = None, pos_start = None, pos_end = None):
        self.tokenType = type
        self.tokenValue = value
        self.pos_start = pos_start.copy()
        self.pos_end = pos_start.copy()
        self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        if self.tokenValue:
            return f'{self.tokenType}:{self.tokenValue}'
        return f'{self.tokenType}'

###########
#POSTION
###########

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.ln += 1
            self.col = 0

        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


###########
#ERROR
###########

class Error:
    def __init__(self, errName, errDetails, pos_start, pos_end):
        self.errName = errName
        self.errDetails  = errDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg = f'{self.errName}: {self.errDetails}\n'
        errMsg += f'File: {self.pos_start.fn}, Line {self.pos_start.ln}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg
    
class InvalidCharErr(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidCharErr", errDetails, pos_start, pos_end)

###########
#LEXER
###########

class Lexer:
    def __init__(self, ftxt, fn):
        self.ftxt = ftxt
        self.fn = fn
        self.currentChar = None
        self.position = Position(-1, 0, -1, fn, ftxt)
        self.advance()

    def advance(self):
        self.position.advance()
        self.currentChar = self.ftxt[self.position.idx] if self.position.idx < len(self.ftxt) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Tokens(TT_PLUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Tokens(TT_MINUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Tokens(TT_MUL, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Tokens(TT_DIV, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Tokens(TT_LPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Tokens(TT_RPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                currentChar = self.currentChar
                currentPos = self.position.copy()
                self.advance()
                return None, InvalidCharErr("'" + currentChar + "'", currentPos, self.position)
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
            return Tokens(TT_FLOAT, float(num_str), pos_start, self.position)
        else:
            return Tokens(TT_INT, int(num_str), pos_start, self.position)
        

###########
#NODES
###########

class NumberNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self):
        return f'{self.token}'

class BinaryNode:
    def __init__(self, leftNode, op_token, rightNode):
        self.leftNode = leftNode
        self.op_token = op_token
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.leftNode},{self.op_token},{self.rightNode})'

class UnaryNode:
    def __init__(self, op_token, rightNode):
        self.op_token = op_token
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.op_token}, {self.rightNode})'
    
###########
#PARESE RESULT
###########

class ParseResult:
    def __init__(self):
        self.node = None
        self.err = None

#register returns node, if there is err in input, it assigns to parseResult instance
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.err:
                self.err = res.err
            return res.node
        return res
    
    def success(self, node):
        self.node = node
        return self
    
    def error(self, err):
        self.err = err
        return self
    
###########
#PARSE
###########

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.currentToken = None
        self.index =-1
        self.advance()

    def advance(self):
        self.index += 1
        self.currentToken = self.tokens[self.index] if self.index < len(self.tokens) else None
        return self

    def expression(self):
        pass

    def term(self):
        pass

    def factor(self):
        token = self.currentToken
        parseResult = ParseResult()

        if token.tokenType in (TT_INT, TT_FLOAT):
            #advance and return number node obj
            self.advance()
            return parseResult.success(NumberNode(token))

    def parse(self):
        pass


###########
#RUN
###########

def run(fn, ftxt):
    
    #create lexer
    lexer = Lexer(ftxt, fn)
    tokens, error = lexer.makeTokens()

    return tokens, error
