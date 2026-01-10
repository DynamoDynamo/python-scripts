
from strings_with_arrows import *

#TASK: tokenize input
#TASK: arrange tokens into organized nodes for execution

############
#TOKENS
############
DIGITS = '0123456789'
DOT = '.'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'

class Token:
    def __init__(self, tokentype, tokenValue = None, pos_start = None, pos_end = None,):
        self.type = tokentype
        self.value = tokenValue
        self.pos_start = pos_start.copy()
        self.pos_end = pos_start.copy()
        self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'
        
############
#POSITION
############

class Position:
    def __init__(self, idx, col, ln, fname, ftxt):
        self.idx = idx
        self.col = col
        self.ln = ln
        self.fname = fname
        self.ftxt = ftxt

    def __repr__(self):
        return f'{self.ln}, {self.idx}, {self.col}'

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.col = 0
            self.ln += 1
    
    def copy(self):
        return Position(self.idx, self.col, self.ln, self.fname, self.ftxt)
        
############
#Error
############

class Error:
    def __init__(self, errorName, errorDetails, pos_start, pos_end):
        self.errName = errorName
        self.errDetails = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg = f'{self.errName}: {self.errDetails}\n'
        errMsg += f'File{self.pos_start.fname}, Line{self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg
    
class InvalidCharErr(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("InvalidCharErr", errorDetails, pos_start, pos_end)

class InvalidSyntaxErr(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("InvalidSyntaxErr", errorDetails, pos_start, pos_end)


############
#LEXER
############

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.currentChar = None
        self.position = Position(-1, -1, 0, fileName, userInput)
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar !=  None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TT_MUL, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(TT_DIV, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                currentChar = self.currentChar
                currentPos = self.position.copy()
                self.advance()
                return None, InvalidCharErr("'" + currentChar + "'", currentPos, self.position)
        tokens.append(Token(TT_EOF, pos_start=self.position.copy()))
        return tokens, None


    def makeNumberTokens(self):
        num_str = ''
        dot_count = 0
        startPos = self.position.copy()

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()
        
        if dot_count == 1:
            return Token(TT_FLOAT, float(num_str), startPos, self.position)
        else:
            return Token(TT_INT, int(num_str), startPos, self.position)
        
############
#NODES
############

class NumberNode:
    def __init__(self, tok):
        self.token = tok

    def __repr__(self):
        return f'{self.token}'
    
class BinaryNode:
    def __init__(self, leftNode, op_tok, rightNode):
        self.leftNode = leftNode
        self.op_tok = op_tok
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.leftNode}, {self.op_tok}, {self.rightNode})'

class UnaryNode:
    def __init__(self, op_tok, rightNode):
        self.op_tok = op_tok
        self.rightNode = rightNode

    def __repr__(self):
        return f'{self.op_tok}, {self.rightNode}'
    
############
#PARSERESULT
############

class ParseResult:
    def __init__(self):
        self.node = None
        self.error = None

    def register(self, result):
        if isinstance(result, ParseResult):
            if result.error:
                self.error = result.error
            return result.node
        return result

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self
        
############
#PARSER
############

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.currentToken = None
        self.tokIdx = -1
        self.advance()

    def advance(self):
        self.tokIdx += 1
        self.currentToken = self.tokens[self.tokIdx] if self.tokIdx < len(self.tokens) else None
        return self.currentToken

    def factor(self):
        currentToken = self.currentToken
        result = ParseResult()

        #isCurrentToken a int or float
        if currentToken.type in (TT_INT, TT_FLOAT):
            #advance and return numbertoken
            result.register(self.advance())
            return result.success(NumberNode(currentToken))
        elif currentToken.type in (TT_PLUS, TT_MINUS):
            #advance and return factor
            result.register(self.advance())
            factor = result.register(self.factor())
            if result.error:
                return result
            return result.success(UnaryNode(currentToken, factor))
        elif currentToken.type in (TT_LPAREN):
            #advance and get expression
            result.register(self.advance())
            expr = result.register(self.expression())
            if result.error:
                return result
            if self.currentToken.type == TT_RPAREN:
                result.register(self.advance())
                return result.success(expr)
            else:
                return result.failure(
                    InvalidSyntaxErr("Expected ) right paran", self.currentToken.pos_start, self.currentToken.pos_end)
                )
        return result.failure(
            InvalidCharErr("Expected int or float number", currentToken.pos_start, currentToken.pos_end)
        )


    def term(self):
        return self.binOp(self.factor, (TT_MUL, TT_DIV))

    def expression(self):
        return self.binOp(self.term, (TT_PLUS, TT_MINUS))

    def binOp(self, func, ops):
        parseResult = ParseResult()
        leftNode = parseResult.register(func())
        if parseResult.error:
            return parseResult

        while self.currentToken.type in ops:
            op_tok = self.currentToken
            parseResult.register(self.advance())
            rightNode = parseResult.register(func())
            if parseResult.error:
                return parseResult
            leftNode = BinaryNode(leftNode, op_tok, rightNode)
        return parseResult.success(leftNode)
    
    def parse(self):
        result = self.expression()
        if not result.error and self.currentToken.type != TT_EOF:
            return result.failure(
                InvalidSyntaxErr("Expected + - * /", self.currentToken.pos_start, self.currentToken.pos_end))
        return result
        
############
#RUN
############
def run(userInput, fname):
    #create Lexer instance
    lexer  = Lexer(userInput, fname)
    tokens, error = lexer.makeTokens()

    if error:
        return None, error

    #create Abstract syntax tokens
    parser = Parser(tokens)
    result = parser.parse()

    return result.node, result.error

