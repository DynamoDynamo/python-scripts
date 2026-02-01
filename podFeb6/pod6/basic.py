
from strings_with_arrows import *

#TASK: tokenize input for mathsymbol, paran
#TASK: create error with Pos, if input is not in tokens

#TASK: organize tokens through interpreter inorder of execution

###########
#TOKENS
###########

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_POW = 'POW'

DIGITS = '0123456789'
TT_EOF = 'EOF'

class Tokens:
    def __init__(self, type, value=None, pos_start = None, pos_end = None):
        self.type = type
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advancePos()
        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'


#############
#ERROR
#############
class Error:
    def __init__(self, errorName, errorDetails, pos_start, pos_end):
        self.errName = errorName
        self.errDetails = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg = f'{self.errName}:{self.errDetails}\n'
        errMsg += f'File {self.pos_start.fileName}, Line {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.userInput, self.pos_start, self.pos_end)
        return errMsg


############
#IllegalCharErr
############
class IllegalCharError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("IllegalCharError", errorDetails, pos_start, pos_end)

#############
#POSITION
#############

class Position:
    def __init__(self, line, col, index, fileName, userInput):
        self.ln = line
        self.col = col
        self.idx = index
        self.fileName = fileName
        self.userInput = userInput

    def advancePos(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.col = 0
            self.ln + 1
        return self
    
    def __repr__(self):
        return f'{self.ln}:{self.col}:{self.idx}'

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.fileName, self.userInput)
    

##########
#LEXER - make tokens
##########

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fileName = fileName
        self.position = Position(0, -1, -1, fileName, userInput)
        self.currentChar = None
        self.advance()
    
    def advance(self):
        self.position.advancePos()
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Tokens(TT_PLUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Tokens(TT_MINUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Tokens(TT_MUL, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Tokens(TT_DIV, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Tokens(TT_LPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Tokens(TT_RPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '^':
                tokens.append(Tokens(TT_POW, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                #return error
                currentPos = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, IllegalCharError(f'{currentChar} not in available tokens', pos_start=currentPos, pos_end=self.position)
        tokens.append(Tokens(TT_EOF))
        return tokens, None


    def makeNumberTokens(self):
        num_str = ''
        dot_count = 0
        pos_start=self.position.copy()
        while self.currentChar != None and self.currentChar in DIGITS + '.':
            if self.currentChar == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()

        if dot_count == 0:
            return Tokens(TT_INT, int(num_str), pos_start=pos_start, pos_end=self.position)
        return Tokens(TT_FLOAT, float(num_str), pos_start=pos_start, pos_end=self.position)
    
#############
#INTERPRETER
#############

class NumberNode:
    def __init__(self, numberToken):
        self.numToken = numberToken

    def __repr__(self):
        return f'{self.numToken}'
    
class BinaryNode:
    def __init__(self, leftNode, op_token, right_node):
        self.leftNode = leftNode
        self.op_token = op_token
        self.rightNode = right_node

    def __repr__(self):
        return f'({self.leftNode}, {self.op_token}, {self.rightNode})'
    
class UnaryNode:
    def __init__(self, op_token, rightNode):
        self.op_token = op_token
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.op_token},{self.rightNode})'
    
############
#Parser
############

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        self.index += 1
        self.currentToken = self.tokens[self.index] if self.index < len(self.tokens) else None

    def atom(self):
        #return numberNode
        currentToken = self.currentToken

        if currentToken.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(currentToken)
        elif currentToken.type == TT_LPAREN:
            self.advance()
            expr = self.expr()
            if self.currentToken.type == TT_RPAREN:
                self.advance()
                return expr
            
    def factor(self):
         currentToken = self.currentToken
         if currentToken.type in (TT_PLUS, TT_MINUS):
            self.advance()
            return UnaryNode(currentToken, self.factor())
         return self.power()
            
    def power(self):
        return self.bin_op(self.atom,  self.factor, (TT_POW))
        
    def term(self):
        return self.bin_op(self.factor, None, (TT_MUL, TT_DIV))
    
    def expr(self):
        return self.bin_op(self.term, None, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, funcA, funcB, opTokens):
        if funcB == None:
            funcB = funcA
        leftNode = funcA()
        while self.currentToken.type in opTokens:
            op_token = self.currentToken
            self.advance()
            rightNode = funcB()
            leftNode = BinaryNode(leftNode, op_token, rightNode)
        return leftNode

        
    def getParsedExpr(self):
        return self.expr(), None

    
###########
#RUN
##########

def run(userInput, fileName):
    
    #crate lexer instance and make tokens
    lexerInstance = Lexer(userInput, fileName)
    tokens, error = lexerInstance.makeTokens()

    if error:
        return None, error

    #Create Parser instance and orgaize tokens into nodes
    print(f'lexer tokens: {tokens}')
    parser = Parser(tokens)
    result, error = parser.getParsedExpr()

    return result, error
