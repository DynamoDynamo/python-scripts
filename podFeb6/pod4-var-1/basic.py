
from strings_with_arrows import *

# TASK: tokenize userinput
# TASK: add position to error
# TASK: segregate tokens into nodes for execution
# TASK: calculate 
# TASK: add division error
# TASK: add context

#############
#TOKENS
#############

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_EOF = 'EOF'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_POW = 'POW'
DOT = '.'
DIGITS = '0123456789'

class Token:
    def __init__(self, type, value=None, pos_start = None, pos_end = None):
        self.tokenType = type
        self.tokenValue = value
        self.pos_start =  pos_start.copy()
        self.pos_end = pos_start.copy()
        self.pos_end = self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.tokenValue:
            return f'{self.tokenType}:{self.tokenValue}'
        else:
            return f'{self.tokenType}'
        
###########
#POSITION
###########

class Position:
    def __init__(self, line, col, index, fileName, fileText):
        self.ln = line
        self.col = col
        self.idx = index
        self.fn =fileName
        self.ftxt = fileText

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.col = 0 
            self.ln += 1
        return self
    
    def __repr__(self):
        return f'{self.ln}:{self.col}:{self.idx}'

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.fn, self.ftxt)  
    
###########
#ERROR
###########

class Error:
    def __init__(self, errorName, errDetails, pos_start, pos_end):
        self.errorName = errorName
        self.errDetails = errDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        print(self.pos_start)
        print(self.pos_end)
        errMsg = f'{self.errorName}:{self.errDetails}\n'
        errMsg += f'File{self.pos_start.fn}, Line {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg

class InvalidCharError(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidCharError", errDetails, pos_start, pos_end)

class InvalidSyntaxError(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidSyntaxError", errDetails, pos_start, pos_end)

class RTError(Error):
    def __init__(self, errDetails, pos_start, pos_end, context):
        super().__init__("RTError", errDetails, pos_start, pos_end)
        self.context = context

    def __repr__(self):
        errMsg = self.generate_traceback()
        errMsg += f'{self.errorName}:{self.errDetails}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg
    
    def generate_traceback(self):
        traceBack = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            traceBack += f'File {pos.fn}, Line {pos.ln + 1}, in {ctx.display_name}\n'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        return 'Traceback (most recent calls):\n' + traceBack


###########
#LEXER
###########

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.fileName = fileName
        self.currentChar = None
        self.position = Position(0, -1, -1, fileName, userInput)
        self.advance()

# advance and assign currentChar
    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

# create tokens
    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
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
            elif self.currentChar == '^':
                tokens.append(Token(TT_POW, pos_start=self.position.copy()))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumuberTokens())
            else:
                # if currChar is not a number or math symbol or () return error
                start_pos = self.position.copy()
                currentChar = self.currentChar
                self.advance()
                return None, InvalidCharError("'"+ currentChar +"'", start_pos, self.position)
        tokens.append(Token(TT_EOF, pos_start=self.position.copy()))
        return tokens, None


    def makeNumuberTokens(self):
        num_str = ''
        dot_count = 0
        start_pos = self.position.copy()

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()
        
        if dot_count == 1:
            return Token(TT_FLOAT, float(num_str), pos_start=start_pos, pos_end=self.position)
        else:
            return Token(TT_INT, int(num_str), pos_start=start_pos, pos_end=self.position)
        
###########
#NODES
###########

class NumberNode:
    def __init__(self, token):
        self.numberNode = token
        self.pos_start =  token.pos_start
        self.pos_end = token.pos_end
        
    def __repr__(self):
        return f'{self.numberNode}'
    
class BinaryNode:
    def __init__(self, leftNode, op_token, rightNode):
        self.leftNode = leftNode
        self.op_token = op_token
        self.rightNode = rightNode

        self.pos_start = leftNode.pos_start
        self.pos_end = rightNode.pos_end

    def __repr__(self):
        return f'({self.leftNode},{self.op_token},{self.rightNode})'
    
class UnaryNode:
    def __init__(self, op_token, rightNode):
        self.op_token = op_token
        self.rightNode = rightNode

        self.pos_start =  op_token.pos_start
        self.pos_end = rightNode.pos_end

    def __repr__(self):
        return f'({self.op_token}, {self.rightNode})'
    
##############..
#PARSERESULT
##############

class ParseResult:
    def __init__(self):
        self.node = None
        self.error = None

#returns node, assigns the -ve side, and returns the +ve side
    def register(self, response):
        if isinstance(response, ParseResult):
            #check if err and assign it
            if response.error:
                self.error = response.error
            return response.node
        return response
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self

    
###########
#PARSER
###########

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIdx = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        #advance
        self.tokenIdx += 1
        #assignCurrent token
        self.currentToken = self.tokens[self.tokenIdx] if self.tokenIdx < len(self.tokens) else None
        return self.currentToken

    def factor(self):
        parseResult = ParseResult()
        currentToken = self.currentToken

        if currentToken.tokenType in (TT_INT, TT_FLOAT):
            parseResult.register(self.advance())
            return NumberNode(currentToken)
        elif currentToken.tokenType in (TT_PLUS, TT_MINUS):
            parseResult.register(self.advance())
            factor = parseResult.register(self.factor())
            if parseResult.error:
                return parseResult
            return parseResult.success(UnaryNode(currentToken, factor))
        elif currentToken.tokenType == TT_LPAREN:
            parseResult.register(self.advance())
            expr = parseResult.register(self.expression())
            if parseResult.error:
                return parseResult
            if self.currentToken.tokenType == TT_RPAREN:
                parseResult.register(self.advance())
                return parseResult.success(expr)
            else:
                return parseResult.failure(InvalidCharError("')' right paran is missing", currentToken.pos_start, self.currentToken.pos_end))
        else:
            return parseResult.failure(InvalidCharError("Int or float number is missing", currentToken.pos_start, currentToken.pos_end))
        
    def power(self):
        return self.binOp(self.factor, (TT_POW))
        
    def term(self):
        return self.binOp(self.power, (TT_DIV, TT_MUL))
    
    def expression(self):
        return self.binOp(self.term, (TT_PLUS, TT_MINUS))

    def binOp(self, func, opTokens):
        parseResult = ParseResult()
        left = parseResult.register(func())
        if parseResult.error:
            return parseResult

        while self.currentToken.tokenType in opTokens:
            op_token = self.currentToken
            parseResult.register(self.advance())
            right = parseResult.register(func())
            if parseResult.error:
                return parseResult
            left = BinaryNode(left, op_token, right)
        return parseResult.success(left)
    
    def parse(self):
        parseResult = self.expression()

        if self.currentToken.tokenType != TT_EOF and not parseResult.error:
            return parseResult.failure(InvalidSyntaxError("+ or - or / or * is missing", self.currentToken.pos_start, self.currentToken.pos_end))
        return parseResult
    
##########
#NUMBER
##########

class PNumber:

    def __init__(self, number):
        self.value = number
        self.setContext()

    def setPos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

        return self
    
    #the new calculated numbers are given context
    def setContext(self, context = None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.value + other.value).setContext(self.context), None
    
    def subbed_by(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.value - other.value).setContext(self.context), None

    def multed_to(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.value * other.value).setContext(self.context), None

    def divided_by(self, other):
        if isinstance(other, PNumber):
            if other.value == 0:
                return None, RTError("Division by zero", other.pos_start, other.pos_end, self.context)
            return PNumber(self.value / other.value).setContext(self.context), None
        
    def powered_by(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.value ** other.value).setContext(self.context), None

    def __repr__(self):
        return f'{self.value}'
    
##########
#IRESULT
##########

class InterpreterResult:

    def __init__(self):
        self.result = None
        self.error = None

    def register(self, response):
        if response.error:
            self.error = response.error
        return response.result
    
    def success(self, pNumber):
        self.result  = pNumber
        return self

    def failure(self, error):
        self.error = error
        return self

##########
#INTERPRETER
##########

class Interpreter:
    def visit(self, node, context):
        typeOfNode = type(node).__name__ #this will give the class of obj
        methodName = getattr(self, f'visit_{typeOfNode}', self.visit_ErrNode)
        return methodName(node, context)
    
    def visit_ErrNode(self, node, context):
        raise Exception(f'visit_{type(node).__name__ } is defined')

    def visit_NumberNode(self, node, context):
        #each number is given context
        numberNode = node.numberNode
        return InterpreterResult().success(
            PNumber(numberNode.tokenValue)
            .setPos(node.pos_start, node.pos_end)
            .setContext(context)
            )


    def visit_BinaryNode(self, node, context):
        iResult = InterpreterResult()
        rightNode = node.rightNode
        rightNumber = iResult.register(self.visit(rightNode, context))
        if iResult.error:
            return iResult
        leftNode = node.leftNode
        leftNumber = iResult.register(self.visit(leftNode, context))
        if iResult.error:
            return iResult
        op_token_type = node.op_token.tokenType

        if op_token_type == TT_PLUS:
            #add
            result, error = leftNumber.added_to(rightNumber)

        elif op_token_type == TT_MINUS:
            #sub
            result, error = leftNumber.subbed_by(rightNumber)

        elif op_token_type == TT_MUL:
            #mul
            result, error = leftNumber.multed_to(rightNumber)
        elif op_token_type == TT_DIV:
            #div
            result, error = leftNumber.divided_by(rightNumber)
        elif op_token_type == TT_POW:
            #pow
            result, error = leftNumber.powered_by(rightNumber)

        if error:
            return iResult.failure(error)
        return iResult.success(
            result.setPos(node.pos_start, node.pos_end)
            )

    def visit_UnaryNode(self, node, context):
        iResult = InterpreterResult()
        rightNode = node.rightNode
        rightNumber = iResult.register(self.visit(rightNode, context))
        if iResult.error:
            return iResult
        op_token_type = node.op_token.tokenType

        if op_token_type == TT_MINUS:
            rightNumber, error = rightNumber.multed_to(PNumber(-1))
        if error:
            return iResult.failure(error)
        return iResult.success(
            rightNumber.setPos(node.pos_start, node.pos_end)
            )
    
###########
#CONTEXT
###########

class Context:
    def __init__(self, display_name, parent = None, parent_entry_pos = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        
##########
#RUN
##########

def run(userInput, fileName):
    
    #create lexer instance

    lexer = Lexer(userInput, fileName)
    
    #create tokens
    tokens, error =  lexer.makeTokens()

    if error:
        return None, error
    
    #create Parser instance
    parser = Parser(tokens)
    print(tokens)

    # create AST Abstract Syntax Tokens
    ast = parser.parse()

    if ast.error:
        return None, ast.error

    #create Interpreter instance
    interpreter = Interpreter()
    print(ast.node)

    #create context
    context = Context('<programe>')

    #calcualate result
    iResult = interpreter.visit(ast.node, context)

    

    return iResult.result, iResult.error

