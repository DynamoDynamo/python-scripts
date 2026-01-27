from strings_with_arrows import *


#TASK: Tokenize input
#TASK: Parser - to organize tokens for execution
#TASK: add Error
#TASK: Interpreter - calcualte organized tokens

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
    def __init__(self, tokenType, tokenValue = None, pos_start = None, pos_end = None):
        self.type = tokenType
        self.value = tokenValue
        self.pos_start = pos_start.copy()
        self.pos_end = self.pos_start.copy()
        self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end
        

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

class InvalidsyntaxError(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidsyntaxError", errDetails, pos_start, pos_end)

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
                tokens.append(Tokens(TT_PLUS, pos_start = self.position.copy()))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Tokens(TT_MINUS, pos_start = self.position.copy()))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Tokens(TT_MUL, pos_start = self.position.copy()))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Tokens(TT_DIV, pos_start = self.position.copy()))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Tokens(TT_LPAREN, pos_start = self.position.copy()))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Tokens(TT_RPAREN, pos_start = self.position.copy()))
                self.advance()
            elif self.currentChar == '^':
                tokens.append(Tokens(TT_POW, pos_start = self.position.copy()))
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
        tokens.append(Tokens(TT_EOF, pos_start=self.position))
        return tokens, None

    def makeNumberToken(self):
        num_str = ''
        dot_cout = 0
        pos_start = self.position.copy()

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_cout == 1:
                    break
                dot_cout += 1
            num_str += self.currentChar
            self.advance()
        
        if dot_cout == 1:
            return Tokens(TT_FLOAT, float(num_str), pos_start=pos_start, pos_end=self.position)
        return Tokens(TT_INT, int(num_str), pos_start=pos_start, pos_end=self.position)
    

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
#ParseResult
###############

class ParseResult:

    def __init__(self):
        self.node = None
        self.error = None

    def register(self, resObj):
        if isinstance(resObj, ParseResult):
            if resObj.error:
                self.error = resObj.error
            return resObj.node
        return resObj

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self
    
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
        parseResult = ParseResult()
        currentToken = self.currentToken

        if currentToken.type in (TT_INT, TT_FLOAT):
            self.advance()
            return parseResult.success(NumberNode(currentToken))
        elif currentToken.type in (TT_PLUS, TT_MINUS):
            self.advance()
            atom = parseResult.register(self.atom())
            if parseResult.error:
                return parseResult
            return parseResult.success(UnaryNode(currentToken, atom))
        else:
            return parseResult.failure(InvalidCharError("required int or float or unaryNumber", currentToken.pos_start, currentToken.pos_end))
            
    def paranExpr(self):
        parseResult = ParseResult()
        currentToken = self.currentToken
        if currentToken.type == TT_LPAREN:
            self.advance()
            exprInsideParan = parseResult.register(self.expr())
            if parseResult.error:
                return parseResult
            if self.currentToken.type == TT_RPAREN:
                self.advance()
                return parseResult.success(exprInsideParan)
            else:
                return parseResult.failure(InvalidsyntaxError("'(' symbol required", currentToken.pos_start, self.currentToken.pos_end))
        return self.atom()
        
    def pow(self):
        return self.bin_op(self.paranExpr, (TT_POW)) 

    def term(self):
        return self.bin_op(self.pow, (TT_MUL, TT_DIV))


    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, funcA, opTokens):
        parseResult = ParseResult()
        left = parseResult.register(funcA())
        if parseResult.error:
            return parseResult
        while self.currentToken.type in opTokens:
            op_token = self.currentToken
            self.advance()
            right = parseResult.register(funcA())
            if parseResult.error:
                return parseResult
            left  = BinaryNode(left, op_token, right)
        return parseResult.success(left)

    def parser(self):
        parseResult = self.expr()
        if self.currentToken.type != TT_EOF and not parseResult.error:
            return parseResult.failure(InvalidsyntaxError("math symbol required", self.currentToken.pos_start, self.currentToken.pos_end))
        return parseResult
    
###############
#NUMBER
###############

class PNumber:

    def __init__(self, number):
        self.number = number

    def added_to(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number + other.number)
        
    def sub_by(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number - other.number)
        
    def div_by(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number / other.number)
    
    def multed_to(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number * other.number)
    
    def pow_by(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number ** other.number)

###############
#INTERPRETER
###############

class Interpreter:
    
    def visit(self, node):
        typeOfNode = type(node).__name__
        self.methodName = f'visit_{typeOfNode}'
        method = getattr(self, self.methodName, self.no_visit)
        return method(node)
    
    def no_visit(self, node):
        raise Exception(f'visit_{type(node).__name__} method is not available')
    
    #this method returns PNumber
    def visit_NumberNode(self, node):
        return PNumber(node.numToken.value)

    def visit_BinaryNode(self, node):
        leftNum = self.visit(node.leftNode)
        rightNum = self.visit(node.rightNode)
        op_token_type = node.op_tok.type

        if op_token_type == TT_MUL:
            resultNum = leftNum.multed_to(rightNum)
        elif op_token_type == TT_DIV:
            resultNum = leftNum.div_by(rightNum)
        elif op_token_type == TT_POW:
            resultNum = leftNum.pow_by(rightNum)
        elif op_token_type == TT_PLUS:
            resultNum = leftNum.added_to(rightNum)
        elif op_token_type == TT_MINUS:
            resultNum = leftNum.sub_by(rightNum)

        return resultNum

    def visit_UnaryNode(self, node):
        rightNum = self.visit(node.rightNode)
        op_tok_type = node.op_token.type

        if op_tok_type == TT_MINUS:
            rightNum = rightNum.multed_to(PNumber(-1))

        return rightNum


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
    parserObj = Parser(tokens)
    print(f'Tokens: {tokens}')

    parseResult = parserObj.parser()
    if parseResult.error:
        return None, parseResult.error
    
    #create Interpreter instance
    print(parseResult.node)
    interpreter = Interpreter()
    calcualtedNum = interpreter.visit(parseResult.node)
    return calcualtedNum.number, None

