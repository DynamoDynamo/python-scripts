
###############################
#TOKENS
###############################

DIGITS = '0123456789'

###############################
#ERROR
###############################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result =  f'{self.error_name}:{self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result
    
#defining child classes for error
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character ", details)


###############################
#POSITION
###############################

class Position:
    def __init__(self, index, linePos, colPos, fileName, fileText):
        self.index = index
        self.ln = linePos
        self.col = colPos
        self.fn = fileName
        self.fText = fileText

    def advance(self, currentText):
        self.index += 1
        self.col += 1

        if(currentText == '\n'):
            self.ln += 1
            self.col = 0

        return self
    
    def currentPos(self):
        return Position(self.index, self.ln, self.col, self.fn, self.fText)

###############################
#TOKENS
###############################
#TT means TokenType

#This class creates tokens for each number and symbol
#Python has __init__ as default constructor
#self - which is instance of class will be input for everymethod
#__repr__ defines how values of a class will be printed when class is called

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

class Token:
    def __init__(self, tokenType, tokenValue=None):
        self.type = tokenType
        self.value = tokenValue

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
###############################
#LEXER
###############################
#this class process the content into tokens

class Lexer:
    def __init__(self, fileName, content):
        self.fn = fileName
        self.text = content
        #Initial positon is index -1, line 0, col -1
        self.pos = Position(-1, 0, -1, fileName, content)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            #if char is space or tab, do nothing
            if self.current_char in (' \t'):
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_numberToken())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                pos_start = self.pos.currentPos()
                currentChar = self.current_char
                self.advance()
                # v r advancing above that's why self.pos will be diff from pos_start
                return [], IllegalCharError(pos_start, self.pos, "'" + currentChar + "'")
        return tokens, None

    
    def make_numberToken(self):
        dot_count = 0
        number_str = ''

        while self.current_char !=None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                number_str += '.'
            else:
                number_str += self.current_char
            self.advance()
        
        if dot_count == 0:
            return Token(TT_INT, int(number_str))
        else:
            return Token(TT_FLOAT, float(number_str))
        
###############################
#RUN
###############################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error