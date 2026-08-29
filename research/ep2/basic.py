
#############
# TOKENS
#############
from string_with_arrows import string_with_arrows


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

##############
#ERROR
#############
class Error:
    def __init__(self, errorName, errorDetails, pos_start, pos_end):
        self.name = errorName
        self.details = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        result = f'{self.name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}\n'
        result += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):

    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("IllegalCharError", errorDetails, pos_start, pos_end)

########
#POSITION - Captures position of charachter from a single line or multiple lines
############

class Position:
    def __init__(self, ln, col, index, fn, ftxt):
        self.ln = ln
        self.col = col
        self.idx = index
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.fn, self.ftxt)

########
#LEXER - LOGIC TO MAKE TOKENS
############

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fn = fileName
        self.currentChar = None
        self.position = Position(0, -1, -1, fileName, userInput)
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

    def makeTokens(self):

        tokens = []

        while self.currentChar != None:
            #store tokens in tokensArray
            if self.currentChar in '\n\t ':
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
                pos_start = self.position.copy()
                currentChar = self.currentChar
                return None, IllegalCharError(currentChar, pos_start, self.position.advance()) #errorName:errorMsg
        return tokens, None

    def makeNumberTokens(self):
        dot_count = 0
        num_str = ''

        while self.currentChar != None and (self.currentChar in DIGITS or self.currentChar == DOT):
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
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

def run(userInput, fileName):
    #send the input to Lexer and get the tokens
    lexerInstance = Lexer(userInput, fileName)
    tokens,error = lexerInstance.makeTokens()
    return tokens, error