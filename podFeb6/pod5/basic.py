#TASK: Tokenize input

###############
#TOKENS
###############

TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_DIV = "DIV"
TT_MUL = "MUL"
TT_INT = "INT"
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_FLOAT = "FLOAT"
DIGITS = "123456789"
DOT = "."

class Tokens:
    def __init__(self, tokenType, tokenValue = None):
        self.type = tokenType
        self.value = tokenValue

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'
    
###############
#ERROR
###############
class Error:
    def __init__(self, errorName, errDetails):
        self.errorName = errorName
        self.errDetails = errDetails

    def __repr__(self):
        errMsg = f'{self.errorName}:{self.errDetails}\n'
        return errMsg
    
class InvalidCharError(Error):
    def __init__(self, errDetails):
        super().__init__("InvalidCharError", errDetails)
    
###############
#LEXER - makes tokens
###############

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fileName = fileName
        self.currentChar = None
        self.index = -1
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
            elif self.currentChar == '(':
                tokens.append(Tokens(TT_LPAREN))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Tokens(TT_RPAREN))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberToken())
            else:
                #return error
                return None, InvalidCharError(f'{self.currentChar} is invalid')
        #return result
        return tokens, None

    def makeNumberToken(self):
        num_str = ''
        dot_cout = 0

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_cout == 1:
                    break
                dot_cout += 1
            num_str += self.currentChar
            self.advance()
        
        if dot_cout == 1:
            return Tokens(TT_FLOAT, float(num_str))
        return Tokens(TT_INT, int(num_str))
    
def run(userInput, fileName):
    #create lexer instance 
    lexer = Lexer(userInput, fileName)
    return lexer.makeTokens()

