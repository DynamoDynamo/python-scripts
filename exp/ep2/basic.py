###################
#Constants
###################

DIGITS = '0123456789'

###################
#ERROR
###################

class Error:
    def __init__(self, currentPosition, error_name, details):
        self.currentPosition =currentPosition
        self.error_name = error_name
        self.details = details

    def as_string(self):
        return f'{self.error_name}: {self.details}\n File {self.currentPosition.fileName}, Line {self.currentPosition.rowPos + 1}'
    
class IllegalCharError(Error):
    def __init__(self, pos_start, details):
        super().__init__(pos_start, "IllegalCharError", details)

class InvalidSytaxError(Error):
    def __init__(self, pos_start, details):
        super().__init__(pos_start, "Invalid syntax", details)

###################
#Position
#In a text position is defined by
#column, row/line and index is basically col position
#index is used to take out charachter from text
#Can we avoid using index, bcz we have col postion? No, we can't
#Say a text has 3 lines each line has 3 letters with space btw them
# col pos of 1st letter in 2nd line is 0 while index pos is 5
###################

class Position:
    def __init__(self, indexPos, rowPos, colPos, fn, text):
        self.indexPos = indexPos
        self.rowPos = rowPos
        self.colPos = colPos
        self.fileName = fn
        self.text = text

    #Why is it taking current_char?
    #Usually the increment will be on index and col in a line
    #but if current_char is next line, col will be 0 
    #and row pos should be increased by one
    def incrementColAndIndex(self, current_char):
        self.indexPos += 1
        self.colPos += 1

        if(current_char == '\n'):
            self.rowPos += 1
            self.colPos = 0
        return self
    
    def getPositionObj(self):
        return Position(self.indexPos, self.rowPos, self.colPos, self.fileName, self.text)

###################
#Token
###################

TT_INT    = 'INT'
TT_FLOAT  = 'FLOAT'
TT_PLUS   = 'PLUS'
TT_MINUS  = 'MINUS'
TT_MUL    = 'MUL'
TT_DIV    = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}: {self.value}'
        return f'{self.type}'

###################
#Lexer
###################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        #positon of text will start at index -1, row0, col-1
        #what is the purpose of fn
        #fn is a normal text for now, only used for error purpose
        #initialize postion and currentChar
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        #this method in constructor make sure current_char is 
        #picked up at index 0
        self.advancePosAndassignChar()

    def advancePosAndassignChar(self):
        self.pos.incrementColAndIndex(self.current_char)
        self.current_char = self.text[self.pos.indexPos] if self.pos.indexPos < len(self.text) else None

    #defines they data type of each letter
    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advancePosAndassignChar()
            elif self.current_char in DIGITS:
                tokens.append(self.assignNumberToken())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advancePosAndassignChar()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advancePosAndassignChar()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advancePosAndassignChar()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advancePosAndassignChar()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advancePosAndassignChar()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advancePosAndassignChar()
            else:
                #return error
                #get the current position and characther before advancing to next postion
                currentPos = self.pos.getPositionObj()
                currentChar = self.current_char
                self.advancePosAndassignChar()
                return [], IllegalCharError(currentPos, currentChar)

        return tokens, None

    def assignNumberToken(self):
        number_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS +'.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            number_str += self.current_char
            self.advancePosAndassignChar()

        if dot_count == 1:
            return Token(TT_FLOAT, float(number_str))
        else:
            return Token(TT_INT, int(number_str))

###################
#NODE REPRESENTATION
###################
class NumbNode:
    def __init__(self, number):
        self.number = number
        
    def __repr__(self):
        return f'{self.number}'
    
class BinaryOpNode:
    def __init__(self, left_node, operator, right_node):
        self.left_node = left_node
        self.operator = operator
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}{self.operator}{self.right_node})'

###################
#PARSE RESULT
###################
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

#Why are they doing this
#through register and assignError, they are ass self.error
    def register(self, inputObj):
        if isinstance(inputObj, ParseResult):
            if inputObj.error: self.error = inputObj.error
        return inputObj

    def assignNode(self, node):
        self.node = node
        return self
    
    def assignError(self, error):
        self.error = error
        return self

###################
#PARSER
###################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = -1
        self.current_token = self.getNextToken()

    def getNextToken(self):
        self.tokenIndex += 1
        if self.tokenIndex < len(self.tokens):
            return self.tokens[self.tokenIndex]
        return None
    
    def factor(self):
        parseResultObj = ParseResult()
        int_float_token = self.current_token

        if int_float_token.type in (TT_INT, TT_FLOAT):
            self.current_token = self.getNextToken()
            parseResultObj.register(self.current_token)
            return parseResultObj.assignNode(NumbNode(self.current_token))
        
        return parseResultObj.assignError(
            InvalidSytaxError(
               
            )
        )

###################
#RUN
###################

def run(fileName, text):
    lexer = Lexer(fileName,text)
    return lexer.make_tokens()

