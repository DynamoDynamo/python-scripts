#Task1: convert number into tokens
#Task2: return error for illegal chars
#Task3: Give position of that error
#Task4: Organize tokens according to Sytax
    #SubTask: factor number, term */, expression +- < +ve scenario
#Task5: Add IllegalChar error, this requires Tokens to have positions

from string_with_arrows import *
########################
# Position
########################

class Position:
    def __init__(self, index, rowPos, colPos, fileName, userInput):
        self.idx = index
        self.fn = fileName
        self.ftxt = userInput
        self.ln = rowPos
        self.col = colPos

    def advance(self, currentChar):
        self.idx += 1
        self.col += 1
        if currentChar == '\n':
            self.col = 0
            self.ln += 1

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

########################
# ERROR
########################
class Error:
    def __init__(self, errorName, errorDetails, posStart, posEnd):
        self.errorDetails = errorDetails
        self.errorName = errorName
        self.posStart = posStart
        self.posEnd = posEnd
    def __repr__(self):
        errorMsg = f'{self.errorName} {self.errorDetails}\n'
        errorMsg += f'File {self.posStart.fn}, line {self.posStart.ln + 1}'
        errorMsg += '\n\n' + string_with_arrows(self.posStart.ftxt, self.posStart, self.posEnd)
        return errorMsg

class IllegalCharError(Error):
    def __init__(self, errorDetails, posStart, posEnd):
        super().__init__("Illegal character", errorDetails, posStart, posEnd)
    

########################
# TOKENS
########################
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_PLUS = 'PLUS' 
TT_MINUS = 'MINUS'
TT_EOF = 'EOF'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
DIGITS = '0123456789'

class Token:
    def __init__(self, posStart, posEnd, tokenType, tokenValue = None):
        self.tokenType = tokenType
        self.tokenValue = tokenValue
        self.posStart = posStart
        self.posEnd = posEnd

    def __repr__(self):
        if self.tokenValue:
            return f'{self.tokenType}:{self.tokenValue}'
        else:
            return f'{self.tokenType}'
        
########################
# Lexer - makes tokens
########################

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.currentChar = None
        self.position = Position(-1, 0, -1, fileName, userInput)
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None
    
    def makeTokens(self):
        tokens = []
        while self.currentChar != None:
            if self.currentChar in (' \t'):
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
                tokens.append(self.makeNumberTokens())
            else:
                currentPos = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, IllegalCharError(currentChar, currentPos, self.position)
        tokens.append(Token(TT_EOF))
        return tokens, None
        
    
    def makeNumberTokens(self):
        numStr = ''
        dotCount = 0

        while self.currentChar != None and self.currentChar in DIGITS + '.':
            if self.currentChar == '.':
                if dotCount == 1:
                    break
                else:
                    dotCount += 1
            numStr += self.currentChar
            self.advance()
        
        if(dotCount == 1):
            return Token(TT_FLOAT, float(numStr))
        else:
            return Token(TT_INT, int(numStr))
        
########################
# Nodes
########################

class NumberNode:
    def __init__(self, numberToken):
        self.numberToken = numberToken

    def __repr__(self):
        return f'{self.numberToken}'

class BinaryNode:
    def __init__(self, opToken, leftToken, rightToken):
        self.opToken = opToken
        self.leftToken = leftToken
        self.rightToken = rightToken

    def __repr__(self):
        return f'({self.leftToken}, {self.opToken}, {self.rightToken})'
        
########################
# Parser - to organize tokens according to sytax
# create abstract syntax token
########################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        self.index += 1
        self.currentToken = self.tokens[self.index] if self.index < len(self.tokens) else None

    def factor(self):
        token = self.currentToken
        #factor identiefies int or float 
        if token.tokenType in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(token)
        
    def term(self):
        left = self.factor()
        while self.currentToken.tokenType in (TT_MUL, TT_DIV):
            operatorToken = self.currentToken
            self.advance()
            right = self.factor()
            left = BinaryNode(operatorToken, left, right)
        return left
    
    def expression(self):
        left = self.term()
        while self.currentToken.tokenType in (TT_PLUS, TT_MINUS):
            operatorToken = self.currentToken
            self.advance()
            right = self.term()
            left = BinaryNode(operatorToken, left, right)
        return left
    
    def parseTokens(self):
        return self.expression()
        
########################
# Run
########################

def run(userInput, fileName):
    #initiaize lexer
    lexer = Lexer(userInput, fileName)
    tokens, error = lexer.makeTokens()
    if tokens:
        parser = Parser(tokens)
        result = parser.parseTokens()
        return result, None
    else:
        return None, error
            
