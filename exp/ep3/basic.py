from strings_with_arrow import *
################
#ERROR
###############

class Error:
    def __init__(self, pos_start, pos_end, errorName, errorDetails):
        self.errorName = errorName
        self.errorDetails = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errorMsg = f'{self.errorName}:{self.errorDetails}\n'
        errorMsg += f'Line {self.pos_start.ln}, File {self.pos_start.fn}\n'
        errorMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)

        return errorMsg

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, errorDetails):
        super().__init__(pos_start, pos_end, "Illegal Character error", errorDetails)

################
#TOKENS
###############
TT_FLOAT = 'FLOAT'
TT_INT = 'INT'
TT_EOF = 'EOF'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
DIGITS = '0123456789'
DOT = '.'

class Token:
    def __init__(self,pos_start, tokenType, tokenValue = None,  pos_end = None):
        self.type = tokenType
        self.value = tokenValue
        self.pos_start = pos_start
        if pos_end != None:
            self.pos_end = pos_end
        else:
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

    def __repr__(self):
        if self.value != None:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'
################
#POSITION
###############

class Position:
    def __init__(self, idx, col, ln, fn, ftxt):
        self.idx = idx
        self.col = col
        self.ln = ln
        self.fn = fn
        self.ftxt = ftxt
    
    def advance(self, currentChar = None):
        self.idx += 1
        if currentChar == '\n':
            self.ln += 1
            self.col = 0
        else:
            self.col += 1
    
    def copy(self):
        return Position(self.idx, self.col, self.ln, self.fn, self.ftxt)
    
################
#LEXER - lexer makes tokens
###############

class Lexer:
    def __init__(self, fileName, userInput):
        self.fileName = fileName
        self.userInput = userInput
        self.currentChar = None
        self.tokenPos = Position(-1, -1, 0, fileName, userInput)
        self.advance()
    
    def advance(self):
        self.tokenPos.advance()
        self.currentChar = self.userInput[self.tokenPos.idx] if self.tokenPos.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(self.tokenPos, TT_PLUS))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(self.tokenPos, TT_MINUS))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(self.tokenPos, TT_MUL))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(self.tokenPos, TT_DIV))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            elif self.currentChar == '(':
                tokens.append(Token(self.tokenPos, TT_LPAREN))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(self.tokenPos, TT_RPAREN))
                self.advance()
            else:
                currentPos = self.tokenPos.copy()
                currentChar = self.currentChar
                self.advance()
                return None, IllegalCharError(currentPos, self.tokenPos, "'" + currentChar + "'")
        tokens.append(Token(self.tokenPos, TT_EOF))
        return tokens, None
        
        
    def makeNumberTokens(self):
        numStr = ''
        dotCount = 0
        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dotCount == 1:
                    break
                else:
                    dotCount += 1
            numStr += self.currentChar
            self.advance()
        if dotCount == 1:
            return Token(self.tokenPos, TT_FLOAT, float(numStr))
        else:
            return Token(self.tokenPos, TT_INT, int(numStr))

################
#RUN
###############
def run(userInput, fileName):
    lexer = Lexer(fileName, userInput)
    return lexer.makeTokens()
