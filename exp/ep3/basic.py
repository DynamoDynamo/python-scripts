from strings_with_arrow import *

# 1. create tokens out of userInput - Lexer
# 2. create error
# 3. show the position of error, add position only to Error
# 4. create syntax out of tokens - parser for +ve scenario

########################
#TOKENS
########################

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_ADD = 'ADD'
TT_MINUS = 'MINUS'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
DIGITS = '0123456789'

class Tokens:
    def __init__(self, tokenType, tokenValue=None):
        self.tokenType = tokenType
        self.tokenValue = tokenValue

    def __repr__(self):
        if self.tokenValue:
            return f'{self.tokenType}:{self.tokenValue}'
        else:
            return f'{self.tokenType}'
    
#############################
#LEXER - class that actually make tokens
#############################

class Lexer:
    def __init__(self, userInput):
        self.userInput = userInput
        self.currentLetter = None
        self.pos = Position(-1, 0, -1)
        self.advance()
        
    def advance(self):
        self.pos.advance(self.currentLetter)
        self.currentLetter = self.userInput[self.pos.idx] if self.pos.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentLetter != None:
            if self.currentLetter in (' \t'):
                self.advance()
            elif self.currentLetter == '+':
                tokens.append(Tokens(TT_ADD))
                self.advance()
            elif self.currentLetter == '-':
                tokens.append(Tokens(TT_MINUS))
                self.advance()
            elif self.currentLetter == '*':
                tokens.append(Tokens(TT_MUL))
                self.advance()
            elif self.currentLetter == '/':
                tokens.append(Tokens( TT_DIV))
                self.advance()
            elif self.currentLetter == '(':
                tokens.append(Tokens(TT_LPAREN))
                self.advance()
            elif self.currentLetter == ')':
                tokens.append(Tokens( TT_RPAREN))
                self.advance()
            elif self.currentLetter in DIGITS:
                #make number tokens
                tokens.append(self.makeNumberTokens())
            else:
                #Return error
                currentPos = self.pos.copy()
                currentChar = self.currentLetter
                self.advance()
                return None, IllegalCharError("'" + currentChar + "'", self.userInput, currentPos, self.pos )
        tokens.append(TT_EOF)
        return tokens, None
    
    def makeNumberTokens(self):
        numStr = ''
        dotCount = 0
        while self.currentLetter != None and self.currentLetter in DIGITS + '.':
            if self.currentLetter == '.':
                if dotCount == 1:
                    break
                else:
                    dotCount += 1
            numStr += self.currentLetter
            self.advance()
        if dotCount == 1:
            return Tokens( tokenType=TT_FLOAT, tokenValue=float(numStr))
        else:
            return Tokens( tokenType=TT_INT, tokenValue=int(numStr))

########################
#ERROR
########################
class Error:
    def __init__(self, errorMsg, errorType, userInput, posStart, posEnd):
        self.errorMsg = errorMsg
        self.errorType = errorType
        self.userInput = userInput
        self.posStart = posStart
        self.posEnd = posEnd
    
    def __repr__(self):
        error = f'{self.errorMsg} {self.errorType}\n'
        error += string_with_arrows(self.userInput, self.posStart, self.posEnd)
        return error
    
class IllegalCharError(Error):
    def __init__(self, errorMsg, userInput, posStart, posEnd):
        super().__init__(errorMsg, 'Illegal Character', userInput, posStart, posEnd )

########################
#POSITION 
#Assumption: we are dealing with a file of multiple lines
########################

class Position:
    def __init__(self, index, rowPos, colPos):
        self.idx = index
        self.col = colPos
        self.ln = rowPos

    def __repr__(self):
        return f'{self.idx}:{self.ln}:{self.col}'
    
    def advance(self, currentChar = None):
        self.idx += 1
        
        if currentChar == '\n':
            self.col = 0
            self.ln += 1
        else:
            self.col += 1
    
    def copy(self):
        return Position(self.idx, self.ln, self.col)
    
########################
#Parser
########################
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        self.tokenIndex += 1
        self.currentToken = self.tokens[self.tokenIndex] if self.tokenIndex < len(self.tokens) else None
    
    def findFactor(self):
        token = self.currentToken
        if token.tokenType in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(token)


    def findTerm(self):
        left = self.findFactor()
        while self.currentToken.tokenType in (TT_MUL, TT_DIV):
            operator = self.currentToken
            self.advance()
            print('finding right')
            right = self.findFactor()
            left = BinaryNode(left, right, operator)
        return left

    def findExpression(self):
        left = self.findTerm()
        while self.currentToken.tokenType in (TT_ADD, TT_MINUS):
            operator = self.currentToken
            self.advance()
            print('finding right')
            right = self.findTerm()
            left = BinaryNode(left, right, operator)
        return left, None

########################
#Node
########################

class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'
    
class BinaryNode:
    def __init__(self, left, right, operatorToken):
        self.leftNode = left
        self.rightNode = right
        self.operatorToken = operatorToken

    def __repr__(self):
        return f'({self.leftNode},{self.operatorToken},{self.leftNode})'

########################
#Run
########################

def run(userInput):
    lexer = Lexer(userInput)
    tokens, error = lexer.makeTokens()
    parser = Parser(tokens)
    return parser.findExpression()

    