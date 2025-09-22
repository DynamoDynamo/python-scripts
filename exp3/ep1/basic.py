###########################
#Position
###########################

class Position:
     def __init__(self, index, atRow, atCol, userInput, fileName):
          self.index = index
          self.col = atCol
          self.line = atRow
          self.userInput = userInput
          self.fileName = fileName
    
     def advance(self, atChar):
          self.index += 1
          self.col += 1

          if(atChar == '\n'):
               self.line += 1
               self.col = 0
          return self
     
     def getCurrentPos(self):
          return Position(self.index, self.line, self.col, self.userInput, self.fileName)

###########################
#Error
###########################

class Error:
     def __init__(self, posStart, errorName, cause):
          self.pos_start = posStart
          self.errorName = errorName
          self.cause = cause
    
     def __repr__(self):
          return f'{self.errorName}:{self.cause}\n File: {self.pos_start.fileName}, Line{self.pos_start.line + 1} Index{self.pos_start.index + 1}'
     
class IllegalCharError(Error):
     def __init__(self, posStart, cause):
          super().__init__(posStart, 'Illegal Character: ', cause)

###########################
#Digits
###########################

DIGITS = '0123456789'

###########################
#Tokens
###########################

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

class Tokens:
     #TT is TokenType
     def __init__(self, tokenType, tokenValue=None):
          self.tokenType = tokenType
          self.tokenValue = tokenValue
     def __repr__(self):
          if self.tokenValue != None:
               return f'{self.tokenType}:{self.tokenValue}'
          return f'{self.tokenType}'
     
###########################
#Lexer
###########################

class Lexer:
     def __init__(self, fileName, userInput):
          self.userInput = userInput
          self.currentChar = None
          self.pos = Position(-1, 0, -1, userInput, fileName)
          self.advance()

     def advance(self):
          self.pos.advance(self.currentChar)
          self.currentChar = self.userInput[self.pos.index] if self.pos.index < len(self.userInput) else None
 
     def makeNumberTokens(self):
          dotCount = 0
          numbStr = ''
          while self.currentChar != None and self.currentChar in DIGITS + '.':
               if self.currentChar == '.':
                    if dotCount == 1:
                         break;
                    else:
                         dotCount += 1
               numbStr += self.currentChar
               self.advance()
          if(dotCount == 1):
               return Tokens(TT_FLOAT, numbStr)
          else:
               return Tokens(TT_INT, numbStr)

     def makeTokens(self):
          tokens = []
          while(self.currentChar != None):
               if(self.currentChar in ' \t'):
                    self.advance()
               elif(self.currentChar == '+'):
                    tokens.append(Tokens(TT_PLUS))
                    self.advance()
               elif(self.currentChar == '-'):
                    tokens.append(Tokens(TT_MINUS))
                    self.advance()
               elif(self.currentChar == '*'):
                    tokens.append(Tokens(TT_MUL))
                    self.advance()
               elif(self.currentChar == '/'):
                    tokens.append(Tokens(TT_DIV))
                    self.advance()
               elif(self.currentChar == '('):
                    tokens.append(Tokens(TT_LPAREN))
                    self.advance()
               elif(self.currentChar == ')'):
                    tokens.append(Tokens(TT_RPAREN))
                    self.advance()
               elif(self.currentChar in DIGITS):
                    tokens.append(self.makeNumberTokens())
               else:
                    #get the currentPos, currentChar and advance
                    currentPos = self.pos.getCurrentPos()
                    currentChar = self.currentChar
                    self.advance()
                    return None, IllegalCharError(currentPos, currentChar)
          return tokens, None
###########################
#Run
###########################

def run(fileName, userInput):
     lexer = Lexer(fileName, userInput)
     tokens, error = lexer.makeTokens()

     return tokens, error


               
          
          
     
