# TASK: Tokenize input
# TASK: error for input that doesn't have tokens


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

    def __repr__(self):
        errMsg = f'{self.errName}: {self.errorDetails}\n'
        errMsg += f'File {self.pos_start.fileName}, Line {self.pos_start.ln}\n'
        errMsg += string_with_arrows(self.pos_start.userInput, self.pos_start, self.pos_end)
        return errMsg
    
class InvalidCharError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("InvalidCharError", errorDetails, pos_start, pos_end)

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
    def __init__(self, type, value = None):
        self.type = type
        self.value = value 

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
            elif self.currentChar == '^':
                tokens.append(Token(TT_POW))
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
                pos_start = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, InvalidCharError(f"'{currentChar}'", pos_start, self.position)
        tokens.append(Token(TT_EOF))
        return tokens, None
    
    def makeNumberTokens(self):
        numStr = ''
        dotCount = 0
        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dotCount == 1:
                    break
                dotCount += 1
            numStr += self.currentChar
            self.advance()
        if dotCount == 1:
            return Token(TT_FLOAT, float(numStr))
        return Token(TT_INT, int(numStr))
    
############
#RUN
############
def run(userInput, fileName):
    lexerInstance = Lexer(userInput, fileName)
    return lexerInstance.makeTokens()
