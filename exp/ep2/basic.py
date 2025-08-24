###################
#Constants
###################

DIGITS = '0123456789'

###################
#ERROR
###################

class Error:
    def __init__(self, currentPos, error_name, details):
        self.currentPos = currentPos
        self.error_name = error_name
        self.details = details

    def as_string(self):
        return f'{self.error_name}: {self.details}\n File {self.currentPos.fileName}, Line {self.currentPos.rowPos + 1}'
    
class IllegalCharError(Error):
    def __init__(self, currentPos, details):
        super().__init__(currentPos, "IllegalCharError", details)

class InvalidSyntaxError(Error):
    def __init__(self, currentPos, details):
        super().__init__(currentPos, "Invalid System error", details)

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

    def __repr__(self):
        return f'index: {self.indexPos}\nline: {self.rowPos}\ncolumn: {self.colPos}\nfileName: {self.fileName}\ntext: {self.text}'

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
TT_EOF    = 'EOF'
#Why position is used in token class

class Token:
    def __init__(self, type, currentPos=None, value=None):
        self.type = type
        self.value = value
        self.currentPos = currentPos

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
                tokens.append(Token(TT_PLUS, self.pos))
                self.advancePosAndassignChar()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, self.pos))
                self.advancePosAndassignChar()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, self.pos))
                self.advancePosAndassignChar()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, self.pos))
                self.advancePosAndassignChar()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, self.pos))
                self.advancePosAndassignChar()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, self.pos))
                self.advancePosAndassignChar()
            else:
                #return error
                #get the current position and characther before advancing to next postion
                currentChar = self.current_char
                self.advancePosAndassignChar()
                return [], IllegalCharError(self.pos, currentChar)
            
        tokens.append(Token(TT_EOF, self.pos))
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
            return Token(TT_FLOAT, self.pos, value = float(number_str))
        else:
            return Token(TT_INT, self.pos, value = int(number_str))

###################
#NODES
###################

class NumberNode:

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'
    
class BinOpNode:
    def __init__(self, left_node, operator, right_node):
        self.left_node = left_node
        self.right_node = right_node
        self.operator = operator

    def __repr__(self):
        return f'({self.left_node} {self.operator} {self.right_node})'

class UnaryOpNode:
    def __init__(self, operator, right_node):
        self.operator = operator
        self.right_node = right_node

    def __repr__(self):
        return f'({self.operator} {self.right_node})'

###################
#RESULT TO AN OBJECT
###################
class ResultObject:
    def __init__(self):
        self.syntax = None
        self.error = None

    def __repr__(self):
        if(self.error):
            return self.error.as_string()
        return f'{self.syntax}:{self.error}'

    def assignSyntax(self, syntax):
        self.syntax = syntax
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
        self.tok_index = -1
        self.current_token = None
        #as soon as Parser is initialized self.currentToken is int
        self.advanceAndAssignCurrentToken()

    def advanceAndAssignCurrentToken(self):
        self.tok_index += 1
        if self.tok_index < len(self.tokens):
            self.current_token = self.tokens[self.tok_index]
        else: self.current_token = None

    def getFinalParserObject(self):
        expression = self.getExpression()
         # expression = self.getOperation(self.getTerm, (TT_PLUS, TT_MINUS))
        #If expression has no error and currtent_token is not endOfFile
        #then the expression must be in form of continuous numbers
        #like 1 1, which is not a valid expression
        if not expression.error and self.current_token.type != TT_EOF:
            return expression.assignError(
            InvalidSyntaxError(self.current_token.currentPos, "Expected '+', '-', '*', or '/'")
            )
        return expression

#This method advances only if currentToken is a number and returns numberNode form of currenttoken
    def getNumberNodeAndAdvance(self):
        parseResult = ResultObject()
        token = self.current_token
        if(token.type in (TT_INT, TT_FLOAT)):
            self.advanceAndAssignCurrentToken()
            return parseResult.assignSyntax(NumberNode(token))
        #this elif is used if you find +or- instead of number
        elif(token.type == TT_PLUS, TT_MINUS):
            #advance to next token
            self.advanceAndAssignCurrentToken()
            #advance till you find number or error
            parsedNumberNode = self.getNumberNodeAndAdvance()
            #ifError return error
            if parsedNumberNode.error: return parsedNumberNode
            #Elese return UniaryOperator
            return parseResult.assignSyntax(UnaryOpNode(token, parsedNumberNode.syntax))
        #this elif is used if you find ( instead of number
        elif(token.type == TT_LPAREN):
            #if token is LeftParen advance to the next token
            self.advanceAndAssignCurrentToken()
            #get the expression upto till RightParen is encounterd
            expr = self.getExpression()
            #if rightParen is not encountered return Error
            #if encountered andvance to next position and 
            #return expression which will be used as numberNode in term
            if(self.current_token.type == TT_RPAREN):
                self.advanceAndAssignCurrentToken()
                return expr
            else: 
                return parseResult.assignError(
                    InvalidSyntaxError(self.current_token.currentPos, "Expected )")
                    )
        return parseResult.assignError(
            InvalidSyntaxError(self.current_token.currentPos, "Expected int or Float number")
        )
    
    def getExpression(self):
        finalResult = ResultObject()
    #     #left node here is instance of resultObject
    #     #the value is either a number node or error
    #     #if error, return error
        left = self.getTerm() 
        if left.error: return left
        #at this point self.current token is MUL 
        left = left.syntax
        while self.current_token.type in (TT_PLUS, TT_MINUS):
            operator = self.current_token.type
            # advance to number
            self.advanceAndAssignCurrentToken()
            # here right is instance of result object
            # get current number token and advance to next token which is operator
            right = self.getTerm()
            if right.error: return right
            right = right.syntax
            left = BinOpNode(left, operator, right)
        return finalResult.assignSyntax(left)
        
    def getTerm(self):
        finalResult = ResultObject()
        #left node here is instance of resultObject
        #the value is either a number node or error
        #if error, return error
        left = self.getNumberNodeAndAdvance() 
        if left.error: return left
        #at this point self.current token is MUL 
        left = left.syntax
        while self.current_token.type in (TT_MUL, TT_DIV):
            operator = self.current_token.type
            # advance to number
            self.advanceAndAssignCurrentToken()
            # here right is instance of result object
            # get current number token and advance to next token which is operator
            right = self.getNumberNodeAndAdvance()
            if right.error: return right
            right = right.syntax
            left = BinOpNode(left, operator, right)
        return finalResult.assignSyntax(left)
        # return self.getOperation(self.getNumberNodeAndAdvance, (TT_MUL, TT_DIV))
    
    # #Comments for inputs related to getTerm
    # def getOperation(self, func, tokens):
    #     finalResult = ResultObject()
    #     #left node here is instance of resultObject
    #     #the value is either a number node or error
    #     #if error, return error
    #     left = func() 
    #     if left.error: return left
    #     #at this point self.current token is MUL 
    #     left = left.syntax
    #     while self.current_token.type in tokens:
    #         operator = self.current_token.type
    #         # advance to number
    #         self.advanceAndAssignCurrentToken()
    #         # here right is instance of result object
    #         # get current number token and advance to next token which is operator
    #         right = func()
    #         if right.error: return right
    #         right = right.syntax
    #         left = BinOpNode(left, operator, right)
    #     return finalResult.assignSyntax(left)

    
###################
#RUN
###################

def run(fileName, text):
    lexer = Lexer(fileName,text)
    tokens, error =  lexer.make_tokens()
    if error: return None, error

    # generate abstract syntax tree (ast), if there are tokens
    parser = Parser(tokens)
    ast = parser.getFinalParserObject()

    return ast.syntax, ast.error
    # return tokens, None



