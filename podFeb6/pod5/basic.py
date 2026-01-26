from strings_with_arrows import *


#TASK: Tokenize input
#TASK: Parser - to organize tokens for execution

###############
#TOKENS
###############

TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_DIV = "DIV"
TT_MUL = "MUL"
TT_INT = "INT"
TT_POW = "POW"
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_FLOAT = "FLOAT"
DIGITS = "123456789"
TT_EOF = "EOF"
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
    def __init__(self, errorName, errDetails, pos_start, pos_end):
        self.errorName = errorName
        self.errDetails = errDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg = f'{self.errorName}:{self.errDetails}\n'
        errMsg += f'File{self.pos_start.fn}, Line{self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.userInput, self.pos_start, self.pos_end)
        return errMsg
    
class InvalidCharError(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidCharError", errDetails, pos_start, pos_end)

###############
#POSITION
###############

class Position:
    def __init__(self, userInput, fileName, ln, col, idx):
        self.userInput = userInput
        self.fn = fileName
        self.ln = ln
        self.col = col
        self.idx = idx

    def advance(self, currentChar=None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.col = 0
            self.ln += 1

        return self
    
    def copy(self):
        return Position(self.userInput, self.fn, self.ln, self.col, self.idx)
    
###############
#LEXER - makes tokens
###############

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fileName = fileName
        self.currentChar = None
        self.position = Position(userInput, fileName, 0, -1, -1)
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

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
            elif self.currentChar == '^':
                tokens.append(Tokens(TT_POW))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberToken())
            else:
                #return error
                pos_start = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, InvalidCharError(f'"{currentChar}"', pos_start, self.position)
        #return result
        tokens.append(Tokens(TT_EOF))
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
    

###############
#Node
###############

class NumberNode:
    def __init__(self, numToken):
        self.numToken = numToken

    def __repr__(self):
        return f'{self.numToken}'

class BinaryNode:
    def __init__(self, leftNode, op_tok, rightNode):
        self.leftNode = leftNode
        self.op_tok = op_tok
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.leftNode},{self.op_tok},{self.rightNode})'
    
class UnaryNode:
    def __init__(self, op_token, rightNode):
        self.op_token = op_token
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.op_token}, {self.rightNode})'
    
###############
#Parser
###############

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokIdx = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        self.tokIdx += 1
        self.currentToken = self.tokens[self.tokIdx] if self.tokIdx < len(self.tokens) else None

    def atom(self):
        currentToken = self.currentToken

        if currentToken.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(currentToken)
        elif currentToken.type in (TT_PLUS, TT_MINUS):
            self.advance()
            atom = self.atom()
            return UnaryNode(currentToken, atom)
            
    def paranExpr(self):
        currentToken = self.currentToken
        if currentToken.type == TT_LPAREN:
            self.advance()
            exprInsideParan = self.expr()
            if self.currentToken.type == TT_RPAREN:
                self.advance()
                return exprInsideParan
        return self.atom()
        
    def pow(self):
        return self.bin_op(self.paranExpr, (TT_POW)) 

    def term(self):
        return self.bin_op(self.pow, (TT_MUL, TT_DIV))


    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, funcA, opTokens):
        left = funcA()
        while self.currentToken.type in opTokens:
            op_token = self.currentToken
            self.advance()
            right = funcA()
            left  = BinaryNode(left, op_token, right)
        return left

    def parser(self):
        return self.expr(), None

###############
#RUN
###############
    
def run(userInput, fileName):
    #create lexer instance 
    lexer = Lexer(userInput, fileName)
    tokens, error =  lexer.makeTokens()
    if error:
        return None, error
    
    #create parser instance
    parser = Parser(tokens)
    print(f'Tokens: {tokens}')
    return parser.parser()

