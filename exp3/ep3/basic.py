
#1. translate mathematical input to tokens
# 1 + 3 - 5 > INT:1 PLUS INT:3 MINUS INT:5
#2. Add Error
#3. Add Pos to Error
#4. Organize tokens

from string_with_arrow import *


###################
#Tokens
###################
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'

DIGITS = '0123456789'
PERIOD = '.'

class Token:
    def __init__(self, tokenType, posStart, tokenValue = None, posEnd = None):
        self.type = tokenType
        self.value = tokenValue
        self.posStart = posStart
        if(posEnd):
            self.posEnd = posEnd
        else:
            self.posEnd = posStart.copy()
            self.posEnd.advance()

    def __repr__(self):
        repr = f'{self.type}'
        if(self.value):
            repr = f'{self.type}:{self.value}'
        return repr

###################
#Error
###################   

class Error:
    def __init__(self, errorType, errorDetails, posStart, posEnd):
        self.errorType = errorType
        self.errorDetails = errorDetails
        self.posStart = posStart
        self.posEnd = posEnd

    def __repr__(self):
        repr = f'{self.errorType}:{self.errorDetails}\n'
        repr += string_with_arrows(self.posStart.userInput, self.posStart, self.posEnd)
        return repr

class IllegalCharError(Error):

    def __init__(self, errorDetails, posStart, posEnd):
        super().__init__("Illegal character", errorDetails, posStart, posEnd)

###################
#Position
###################

class Position:
    def __init__(self, ln, col, idx, userInput):
        self.ln = ln
        self.col = col
        self.idx = idx
        self.userInput = userInput

    def advance(self, currentChar=None):
        self.idx += 1
        if(currentChar == '\n'):
            self.ln += 1
            self.col = 0
        else:
            self.col += 1

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.userInput)
    
###################
#Node
###################

class NumberNode:
    def __init__(self, numberToken):
        self.numberToken = numberToken

    def __repr__(self):
        return f'{self.numberToken}'
    
class BinaryNode:
    def __init__(self, leftNode, rightNode, opToken):
        self.leftNode = leftNode
        self.rightNode = rightNode
        self.opToken = opToken

    def __repr__(self):
        return f'({self.leftNode}, {self.opToken}, {self.rightNode})'
    
class UnaryNode:
    def __init__(self, opToken, rightNode):
        self.opToken = opToken
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.opToken}, {self.rightNode})'
    
###################
#Parser
###################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIdx = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        self.tokenIdx += 1
        self.currentToken = self.tokens[self.tokenIdx] if self.tokenIdx < len(self.tokens) else None

    def factor(self):
        token = self.currentToken
        print(f'token in factor {self.currentToken}')

        if(token.type in (TT_INT, TT_FLOAT)):
            self.advance()
            return NumberNode(token)

    def term(self):
        leftNode = self.factor()
        while(self.currentToken.type in (TT_MUL, TT_DIV)):
            opToken = self.currentToken
            self.advance()
            rightNode = self.factor()
            leftNode = BinaryNode(leftNode, rightNode, opToken)
        return leftNode

    def expression(self):
        leftNode = self.term()
        while(self.currentToken.type in (TT_PLUS, TT_MINUS)):
            opToken = self.currentToken
            self.advance()
            rightNode = self.term()
            leftNode = BinaryNode(leftNode, rightNode, opToken)

        return leftNode

    def parse(self):
        return self.expression(), None

###################
#Lexer - Lexer translate mathematical input tokens
###################

class Lexer:
    def __init__(self, userInput):
        self.userInput = userInput
        self.index = -1
        self.tokenPos = Position(0, -1, -1, userInput)
        self.currentChar = None
        self.advance()

    def advance(self):
        self.tokenPos.advance()
        self.currentChar = self.userInput[self.tokenPos.idx] if self.tokenPos.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while(self.currentChar != None):
            if(self.currentChar == '+'):
                tokens.append(Token(TT_PLUS, self.tokenPos))
                self.advance()
            elif(self.currentChar == '-'):
                tokens.append(Token(TT_MINUS, self.tokenPos))
                self.advance()
            elif(self.currentChar == '*'):
                tokens.append(Token(TT_MUL, self.tokenPos))
                self.advance()
            elif(self.currentChar == '/'):
                tokens.append(Token(TT_DIV, self.tokenPos))
                self.advance()
            elif(self.currentChar == '('):
                tokens.append(Token(TT_LPAREN, self.tokenPos))
                self.advance()
            elif(self.currentChar == ')'):
                tokens.append(Token(TT_RPAREN, self.tokenPos))
                self.advance()
            elif(self.currentChar in DIGITS):
                tokens.append(self.makeNumberTokens())
            elif(self.currentChar in ' \t'):
                self.advance()
            else:
                #Return error
                currentChar = self.currentChar
                currentPos = self.tokenPos.copy()
                self.advance()
                return None, IllegalCharError(currentChar, currentPos, self.tokenPos)
        tokens.append(Token(TT_EOF, self.tokenPos))
        return tokens, None

    def makeNumberTokens(self):
        numStr = ''
        periodCount = 0
        startPos = self.tokenPos.copy()
        while(self.currentChar != None and self.currentChar in DIGITS + PERIOD):
            if(self.currentChar == PERIOD):
                if(periodCount == 1):
                    break
                else:
                    periodCount += 1
            numStr += self.currentChar
            self.advance()
        
        if(periodCount == 1):
            return Token(TT_FLOAT, startPos, float(numStr), self.tokenPos)
        else:
            return Token(TT_INT, startPos, int(numStr), self.tokenPos)
    

###################
#Run
###################
def run(userInput):
    lexer = Lexer(userInput)
    tokens, error =  lexer.makeTokens()
    if error:
        return None, error
    print(tokens)
    parser = Parser(tokens)
    return parser.parse()

