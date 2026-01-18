
from strings_with_arrows import *

# TASK: tokenize userinput
# TASK: add position to error

#############
#TOKENS
#############

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_EOF = 'EOF'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
DOT = '.'
DIGITS = '0123456789'

class Token:
    def __init__(self, type, value=None, pos_start = None, pos_end = None):
        self.tokenType = type
        self.tokenValue = value
        self.pos_start =  pos_start.copy()
        self.pos_end = self.pos_start.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.tokenValue:
            return f'{self.tokenType}:{self.tokenValue}'
        else:
            return f'{self.tokenType}'
        
###########
#POSITION
###########

class Position:
    def __init__(self, line, col, index, fileName, fileText):
        self.ln = line
        self.col = col
        self.idx = index
        self.fn =fileName
        self.ftxt = fileText

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.col = 0 
            self.ln += 1
        return self

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.fn, self.ftxt)  
    
###########
#ERROR
###########

class Error:
    def __init__(self, errorName, errDetails, pos_start, pos_end):
        self.errorName = errorName
        self.errDetails = errDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg = f'{self.errorName}:{self.errDetails}\n'
        errMsg += f'File{self.pos_start.fn}, Line {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg

class InvalidCharError(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidCharError", errDetails, pos_start, pos_end)

###########
#LEXER
###########

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fileName = fileName
        self.currentChar = None
        self.position = Position(0, -1, -1, fileName, userInput)
        self.advance()

# advance and assign currentChar
    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

# create tokens
    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TT_MUL, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(TT_DIV, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumuberTokens())
            else:
                # if currChar is not a number or math symbol or () return error
                start_pos = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, InvalidCharError("'"+currentChar+"'", start_pos, self.position)
        tokens.append(TT_EOF, pos_start=self.position.copy())
        return tokens, None


    def makeNumuberTokens(self):
        num_str = ''
        dot_count = 0
        start_pos = self.position.copy()

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()
        
        if dot_count == 1:
            return Token(TT_FLOAT, float(num_str), pos_start=start_pos, pos_end=self.position)
        else:
            return Token(TT_INT, int(num_str), pos_start=start_pos, pos_end=self.position)
        
##########
#RUN
##########

def run(userInput, fileName):
    
    #create lexer instance

    lexer = Lexer(userInput, fileName)
    
    #create tokens
    return lexer.makeTokens()

