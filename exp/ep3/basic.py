

#######################
#TOKENS
#######################
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_DIV = 'DIV'

class Token:
    def __init__(self, tokenType, tokenValue = None):
        self.tokenValue = tokenValue
        self.tokenType = tokenType

    def __repr__(self):
        if self.tokenValue != None:
            return '${self.tokenType}:${self.tokenValue}'
        else:
            return '${self.tokenType}'
        
#####################
#Position - position of token
#####################

class Position:
    def __init__(self, idx, col, ln):
        self.idx = idx
        self.col = col
        self.ln =ln

    def advance(self, currentChar=None):
        self.idx += 1
        
        if currentChar == '\n':
            self.ln += 1
            self.col = 0
        else:
            self.col += 1

    def copy(self):
        return Position(self.idx, self.col, self.ln)
        
#####################
#LEXER - lexer creates tokens
#####################

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fileName = fileName
        self.currentChar = None
        self.initialPos = Position(-1, -1, 0)
        self.advance()

    def advance(self):
        self.initialPos.advance()
        self.currentChar = self.userInput[self.initialPos.idx] if self.initialPos.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []
        while self.currentChar != None:
            if self.currentChar == '\t':
                self.advance()
            elif self.currentChar == '+':
                tokens.add(Token(TT_PLUS))
                self.advance()
            elif self.currentChar == '-':
                tokens.add(Token(TT_MINUS))


#######################
#RUN
#######################
def run(userInput, fileName):
    lexer = Lexer(userInput, fileName)
    return lexer.makeTokens()