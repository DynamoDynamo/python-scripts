
#############
# TOKENS
##############
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'

TT_DIV = 'DIV'
TT_MUL = 'MUL'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'

TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

DIGITS = '0123456789'
DOT = '.'

class Token:
    def __init__(self, tokenType, tokenValue = None):
        self.type = tokenType
        self.value = tokenValue

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}' # INT:1, FLOAT:3.3
        return f'{self.type}' #LPAREN, DIV


########
#LEXER - LOGIC TO MAKE TOKENS
############

class Lexer:
    def __init__(self, userInput):
        self.userInput = userInput
        self.currentChar = None
        self.charIndex = -1
        self.advance()

    def advance(self):
        self.charIndex += 1
        self.currentChar = self.userInput[self.charIndex] if self.charIndex < len(self.userInput) else None

    def makeTokens(self):

        tokens = []

        while self.currentChar != None:
            #store tokens in tokensArray
            if self.currentChar in '\t ':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TT_MUL))
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
                #error scenario
                return None, 'errorScenario'
        return tokens, None

    def makeNumberTokens(self):
        dot_count = 0
        num_str = ''

        while self.currentChar != None and (self.currentChar in DIGITS or self.currentChar == DOT):
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            print(self.currentChar)
            num_str += self.currentChar
            self.advance()

        #INT, FLOAT
        if dot_count == 1:
            return Token(TT_FLOAT, float(num_str))
        else:
            return Token(TT_INT, int(num_str))


############
#RUN
#################

def run(userInput):
    #send the input to Lexer and get the tokens
    lexerInstance = Lexer(userInput)
    tokens,error = lexerInstance.makeTokens()
    return tokens, error