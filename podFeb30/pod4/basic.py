from strings_with_arrows import *


# TASK: tokenize userInput
# TASK: give syntax to tokens and arrange them to nodes
# TASK: calcuate nodes, if err, return context


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
            self.pos_end = pos_end

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

    def __repr__(self):
        return f'{self.ln}, {self.idx}, {self.col}'

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
        errMsg += f'File: {self.pos_start.fn}, Line {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg
    
class InvalidCharErr(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidCharErr", errDetails, pos_start, pos_end)

class InvalidSyntaxErr(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidSyntaxErr", errDetails, pos_start, pos_end)

###########
#LEXER
###########

class Lexer:
    def __init__(self, ftxt, fn):
        self.ftxt = ftxt
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
        tokens.append(Tokens(TT_EOF, pos_start=self.position.copy()))
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
    
    def failure(self, err):
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
        return self.currentToken
    
    def factor(self):
        token = self.currentToken
        parseResult = ParseResult()
        if token.tokenType in (TT_INT, TT_FLOAT):
            #advance and return number node obj
            parseResult.register(self.advance())
            return parseResult.success(NumberNode(token))
        if token.tokenType in (TT_PLUS, TT_MINUS):
            #if tokentype is + or - in factor, upcoming expression in unarycode
            parseResult.register(self.advance())
            factor = parseResult.register(self.factor())
            if parseResult.err:
                return parseResult
            return parseResult.success(UnaryNode(token, factor))
        if token.tokenType == TT_LPAREN:
            #if tokentype is left paranthesis, get expression after, check if there is rParen, if not return err
            parseResult.register(self.advance())
            expr = parseResult.register(self.expression())
            if parseResult.err:
                return parseResult
            if self.currentToken.tokenType == TT_RPAREN:
                parseResult.register(self.advance())
                return parseResult.success(expr)
            return parseResult.failure(InvalidSyntaxErr("required ) right paren", self.currentToken.pos_start, self.currentToken.pos_end))
        return parseResult.failure(InvalidCharErr("required int or float", token.pos_start, token.pos_end))


    def expression(self):
        return self.binaryOperation(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.binaryOperation(self.factor, (TT_MUL, TT_DIV))
    
    def binaryOperation(self, func, op_tokens):
        parseResult = ParseResult()
        left = parseResult.register(func())
        if parseResult.err:
            return parseResult
        while(self.currentToken.tokenType in op_tokens):
            op_tok = self.currentToken
            parseResult.register(self.advance())
            right = parseResult.register(func())
            if parseResult.err:
                return parseResult
            left = BinaryNode(left, op_tok, right)
        return parseResult.success(left)

    def parse(self):
        parsedResult = self.expression()
        if not parsedResult.err and self.currentToken.tokenType != TT_EOF:
            return parsedResult.failure(
                InvalidSyntaxErr("required + - * /", self.currentToken.pos_start, self.currentToken.pos_end)
            )
        return parsedResult


###########
#RUN
###########

def run(fn, ftxt):
    
    #create lexer
    lexer = Lexer(ftxt, fn)
    tokens, error = lexer.makeTokens()

    if error:
        return None, error
    
    #create Abstract syntax token
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.err:
        return None, ast.err
    
    #calculate, if error, return context
    print(ast.node)

    return ast.node, ast.err
