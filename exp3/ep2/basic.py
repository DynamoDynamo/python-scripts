#Task1: convert number into tokens
#Task2: return error for illegal chars
#Task3: Give position of that error
#Task4: Organize tokens according to Sytax
    #SubTask: factor number, term */, expression +- < +ve scenario
#Task5: Add IllegalChar error, this requires Tokens to have positions
#Task6: you cannot directly return error from task 5, Now you need parseResult
        #to wrap up both node and error in object and simplsend the obj

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

    def advance(self, currentChar = None):
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
    def __init__(self, tokenType, posStart, posEnd = None, tokenValue = None):
        self.tokenType = tokenType
        self.tokenValue = tokenValue
        self.posStart = posStart
        if posEnd:
            self.posEnd = posEnd
        else:
            self.posEnd = self.posStart.copy()
            self.posEnd.advance()

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
                tokens.append(Token(TT_PLUS, posStart = self.position))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS, posStart = self.position))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TT_MUL, posStart = self.position))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(TT_DIV, posStart = self.position))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Token(TT_LPAREN, posStart = self.position))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TT_RPAREN, posStart = self.position))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                currentPos = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, IllegalCharError(currentChar, currentPos, self.position)
        tokens.append(Token(TT_EOF, posStart = self.position))
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
            return Token(TT_FLOAT, posStart = self.position, tokenValue = float(numStr))
        else:
            return Token(TT_INT, posStart = self.position, tokenValue = int(numStr))
        
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
# parseResult - to wrap up nodes and error in onebject as output
########################

class ParseResult:
    def __init__(self):
        self.node = None
        self.error = None

    def register(self, result):
        if isinstance(result, ParseResult):
            if result.error:
                self.error = result.error
            return result.node
        return result
    
    def success(self, node):
        self.node = node
        return self 
    
    def failure(self, error):
        self.error = error
        return self
        
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
        return self.currentToken

    def factor(self):
        parseResultObj = ParseResult()
        token = self.currentToken
        #factor identiefies int or float 
        if token.tokenType in (TT_INT, TT_FLOAT):
            self.advance()
            return parseResultObj.success(NumberNode(token))
        else: 
            return parseResultObj.failure(IllegalCharError("expected int or float number", token.posStart, token.posEnd))
        
    def term(self):
        termParseResultObj = ParseResult()
        # self.factor() returns ParseResultObj
        # termParseResultObj is a seperateInstance of ParseResultObj
        # if self.factor has error, error gets assigned to termParser
        # if self.factor has node, simply result.node which is of type Token is returned
        left = termParseResultObj.register(self.factor())
        if termParseResultObj.error:
            return termParseResultObj
        
        while self.currentToken.tokenType in (TT_MUL, TT_DIV):
            operatorToken = self.currentToken
            self.advance()
            #right here is token in +ve scenario
            right = termParseResultObj.register(self.factor())
            if termParseResultObj.error:
                return termParseResultObj
            #left here is BinaryNode
            left = BinaryNode(operatorToken, left, right)
        return termParseResultObj.success(left)
    
    def expression(self):
        expressionParseResultObj = ParseResult()
        #self.term() here is always an instance of ParseResultObject()
        #expressionParseResultObj is seperate instance of ParseResultObject()
        #self.term() may return parseResultObj with error or with node
        # if error, register will assign error to expressionParseResultObj
        # if node, it simply returns node, which is of type BinaryNode
        # so left here is always of type BinaryNode, if no error
        # so left may be of type BinaryNode(when no error) or 
        # termParseResultObj if error, that's why we r dealing with
        # expressionParseResultObj when checking the error
        left = expressionParseResultObj.register(self.term())
        if expressionParseResultObj.error:
            return expressionParseResultObj
        while self.currentToken.tokenType in (TT_PLUS, TT_MINUS):
            operatorToken = self.currentToken
            self.advance()
            right = expressionParseResultObj.register(self.term())
            if expressionParseResultObj.error:
                return expressionParseResultObj
            left = BinaryNode(operatorToken, left, right)
        return expressionParseResultObj.success(left)
    
    def parseTokens(self):
        finalParseResultObj = self.expression()
        return finalParseResultObj
        
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
        return result.node, result.error
    else:
        return None, error
            
