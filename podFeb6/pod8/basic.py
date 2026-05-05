#TASK1: Tokenize mathematical input
#TASK2: construct error for bad input

##############
# TOKENS
#############
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
DOT = '.'
DIGITS = '0123456789'

class Tokens:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'
        
#################
# POSITION
#################

class Position:
    def __init__(self, index, col, row, fileName = None, text = None):
        self.index = index
        self.ln = row
        self.col = col
        if fileName:
            self.fileName = fileName
        if text:
            self.text = text


############
#ERROR
#############

class Error:
    pass

###########
# LEXER
############

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.index = -1
        self.currentChar = None
        self.advance()

    def advance(self):
        self.index += 1
        self.currentChar = self.userInput[self.index] if self.index < len(self.userInput) else None

    def makeTokens(self):
        tokens = []
        while self.currentChar != None:
            if self.currentChar in (' ', '\t'):
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Tokens(TT_PLUS))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Tokens(TT_MINUS))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Tokens(TT_MUL))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Tokens(TT_DIV))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                pass
        return tokens, None

    def makeNumberTokens(self):
        dotCount = 0
        numberStr = ''

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if(self.currentChar == DOT):
                if(dotCount == 1):
                    break
                dotCount += 1
            numberStr += self.currentChar
            self.advance()

        if  dotCount == 1:
            return Tokens(TT_FLOAT, float(numberStr))
        else:
            return Tokens(TT_INT, int(numberStr))



##############
#RUN
##############
def run(userInput, fileName):
    lexerInstance = Lexer(userInput, fileName)
    return lexerInstance.makeTokens()