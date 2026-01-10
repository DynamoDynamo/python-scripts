##################
#CONSTANT
##################

DIGITS = '0123456789'

##################
#ERROR
##################

class Error:
    def __init__(self, pos_start, pos_end, errorName, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.errorName = errorName
        self.details = details

    def as_string(self):
        result = f'{self.errorName}: {self.details}\n'
        result += f'File {self.pos_start.fn}, Line {self.pos_start.ln + 1}'
        return result
    
class IllegalCharError(Error):
    def __init__(self,  pos_start, pos_end, details):
        super().__init__( pos_start, pos_end, "IllegalCharError", details)

##################
#POSITION
##################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.col = 0
            self.ln += 1

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

##################
#TOKENS
##################

TT_FLOAT = 'FLOAT'
TT_INT = 'INT'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_EOF = 'EOF'

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    

##################
#LEXER
##################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.currentChar = None
        self.advance()

    def advance(self):
        self.pos.advance(self.currentChar)
        self.currentChar = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
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
                tokens.append(self.make_numberToken())
            else:
                currentPos = self.pos.copy()
                char = self.currentChar
                self.advance()
                return [], IllegalCharError(currentPos, self.pos, "'" + char + "'")
        return tokens, None
                
    def make_numberToken(self):
        num_str = ''
        dot_count = 0
        DOT = '.'

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += DOT
            else:
                num_str += self.currentChar
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        return Token(TT_FLOAT, float(num_str))

##################
#LEXER
##################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    return tokens, error

