
##############
#ERROR
###############

class Error:
    def __init__(self, errorType, errorDetails):
        self.type = errorType
        self.details = errorDetails

    def __repr__(self):
        return f'{self.type}:{self.details}'

class IllegalCharacterError(Error):
    def __init__(self, errorDetails):
        super().__init__("IllegalCharacterError", errorDetails)
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
# LEXER - to convert useriNput to tokens
####################

class Lexer:
    def __init__(self, userInput):
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
                return None, IllegalCharacterError(self.currentChar)
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
#RUN
###############

def run(userInput):
    lexerInstance = Lexer(userInput)
    return lexerInstance.makeTokens()