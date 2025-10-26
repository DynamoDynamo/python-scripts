
##############
#TOKENS
##############
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
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
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def __repr__(self):
        if self.value != None:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'
        
##############
#POSITION 
##############
class Position:
    def __init__(self, idx, col, ln):
        self.idx = idx
        self.col = col
        self.ln = ln
    
    def advance(self, currentChar = None):
        self.idx += 1
        if currentChar == '\n':
            self.ln += 1
            self.col = 0
        else:
            self.col += 1

    def copy(self):
        return Position(self.idx, self.col, self.ln)
##############
#LEXER - lexer makes tokens
##############

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fileName = fileName
        self.currentChar = None
        self.tokenPos = Position(-1, -1, 0)
        self.advance()

    def advance(self):
        self.tokenPos.advance()
        self.currentChar = self.userInput[self.tokenPos.idx] if self.tokenPos.idx < len(self.userInput) else None

    def makeTokes(self):
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
                return None, 'some error'
        tokens.append(Token(TT_EOF))
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
            return Token(TT_FLOAT, float(numStr))
        else:
            return Token(TT_INT, int(numStr))

##############
#RUN
##############

def run(userInput, fileName):
    lexer = Lexer(userInput, fileName)
    result, error = lexer.makeTokes()
    print(result)
    return result, error

