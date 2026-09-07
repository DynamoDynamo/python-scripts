
##############
#ERROR
###############

from string_with_arrows import string_with_arrows

class Error:
    def __init__(self, errorType, errorDetails, pos_start, pos_end):
        self.type = errorType
        self.details = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg =  f'{self.type}:{self.details}\n'
        errMsg += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg

class IllegalCharacterError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__('IllegalCharacterError', errorDetails, pos_start, pos_end)
##############
#TOKENS
###############

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'

DIGITS = '0123456789'
DOT = '.'

TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'

TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

class Token:
    def __init__(self, tokenType, tokenValue = None):
        self.type = tokenType
        self.value = tokenValue

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}' #INT:3, FLOAT:3.3
        else:
            return f'{self.type}' #PLUS,MINUS

#####################
# Position
####################

class Position:
    def __init__(self, line, column, index, fileName, fileContent):
        self.ln = line
        self.col = column
        self.idx =index
        self.fn = fileName
        self.ftxt = fileContent

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if(currentChar == '\n'):
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.fn, self.ftxt)

#####################
# LEXER - to convert useriNput to tokens
####################

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.position = Position(0, -1, -1, fileName, userInput)
        self.currentChar = None
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t\n':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberToken())
            else:
                #ERROR SCENARIO
                pos_start = self.position.copy()
                currentChar = self.currentChar
                return None, IllegalCharacterError(currentChar, pos_start, self.position.advance())
        return tokens, None

    def makeNumberToken(self):
        numStr = ''
        dot_count = 0

        while self.currentChar != None and (self.currentChar in DIGITS or self.currentChar == DOT):
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            numStr += self.currentChar
            self.advance()
        if dot_count == 1:
            return Token(TT_FLOAT, float(numStr))
        else:
            return Token(TT_INT, int(numStr))
#############
#NODES
###############

class NumberNode:
    def __init__(self, numberToken):
        self.token = numberToken

    def __repr__(self):
        return f'{self.token}'

class BinaryOpNode:
    def __init__(self, leftNode, opToken, rightNode):
        self.leftNode = leftNode
        self.opToken = opToken
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.leftNode} {self.opToken} {self.rightNode})'

#############
#PARSER
###############

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.currentToken = None
        self.tokenIndex = -1
        self.advance()

    def advance(self):
        self.tokenIndex += 1
        self.currentToken = self.tokens[self.tokenIndex] if self.tokenIndex < len(self.tokens) else None
        return self.currentToken

    def factor(self):
        token = self.currentToken
        if(token.type in (TT_INT, TT_FLOAT)):
            self.advance()
            return NumberNode(token)

    def term(self):
        return self.binaryOp(self.factor, (TT_MUL, TT_DIV))

    def expression(self):
            return self.binaryOp(self.term, (TT_PLUS, TT_MINUS))

    def binaryOp(self, func, tokenTypes):
        leftNode = func()
        while(self.currentToken != None and self.currentToken.type in tokenTypes):
            opToken = self.currentToken
            self.advance()
            rightNode = func()
            leftNode = BinaryOpNode(leftNode, opToken, rightNode)
        return leftNode

    def parse(self):
        return self.expression(), None

#############
#RUN
###############

def run(userInput, fileName):
    lexerInstance = Lexer(userInput, fileName)
    tokens, error =  lexerInstance.makeTokens()

    if error:
        return None, error

    parserInstance = Parser(tokens)
    return parserInstance.parse()