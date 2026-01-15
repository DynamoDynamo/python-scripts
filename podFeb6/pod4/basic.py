from strings_with_arrows import *


# TASK: tokenize userInput
# TASK: give syntax to tokens and arrange them to nodes
# TASK: calcuate nodes
# TASK: add divided by zero Err
# TASK: context


###########
#TOKENS
###########


TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_EOF = "EOF"
DIGITS = "0123456789"
DOT = "."

class Tokens:
    def __init__(self, type, value = None, pos_start = None, pos_end = None):
        self.tokenType = type
        self.tokenValue = value
        self.pos_start = pos_start.copy()
        self.pos_end = pos_start.copy()
        self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.tokenValue:
            return f'{self.tokenType}:{self.tokenValue}'
        return f'{self.tokenType}'

###########
#POSTION
###########

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def __repr__(self):
        return f'{self.ln}, {self.idx}, {self.col}'

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if currentChar == '\n':
            self.ln += 1
            self.col = 0

        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


###########
#ERROR
###########

class Error:
    def __init__(self, errName, errDetails, pos_start, pos_end):
        self.errName = errName
        self.errDetails  = errDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg = f'{self.errName}: {self.errDetails}\n'
        errMsg += f'File: {self.pos_start.fn}, Line {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg
    
class InvalidCharErr(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidCharErr", errDetails, pos_start, pos_end)

class InvalidSyntaxErr(Error):
    def __init__(self, errDetails, pos_start, pos_end):
        super().__init__("InvalidSyntaxErr", errDetails, pos_start, pos_end)

class RTErr(Error):
    def __init__(self, errDetails, pos_start, pos_end, context):
        super().__init__("RTErr", errDetails, pos_start, pos_end)
        self.context = context

    def __repr__(self):
        errMsg = self.generate_traceback()
        errMsg += f'{self.errName}: {self.errDetails}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg
    
    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result += f'File: {pos.fn}, Line {pos.ln + 1}, in {ctx.display_name}\n'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Traceback (most recent call last):\n' + result
###########
#LEXER
###########

class Lexer:
    def __init__(self, ftxt, fn):
        self.ftxt = ftxt
        self.currentChar = None
        self.position = Position(-1, 0, -1, fn, ftxt)
        self.advance()

    def advance(self):
        self.position.advance()
        self.currentChar = self.ftxt[self.position.idx] if self.position.idx < len(self.ftxt) else None

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
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                currentChar = self.currentChar
                currentPos = self.position.copy()
                self.advance()
                return None, InvalidCharErr("'" + currentChar + "'", currentPos, self.position)
        tokens.append(Tokens(TT_EOF, pos_start=self.position.copy()))
        return tokens, None
    
    def makeNumberTokens(self):
        num_str = ''
        dot_count = 0
        pos_start = self.position.copy()

        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.currentChar
            self.advance()
        
        if dot_count == 1:
            return Tokens(TT_FLOAT, float(num_str), pos_start, self.position)
        else:
            return Tokens(TT_INT, int(num_str), pos_start, self.position)
        

###########
#NODES
###########

class NumberNode:
    def __init__(self, token):
        self.token = token

        self.pos_start = token.pos_start
        self.pos_end = token.pos_end
    def __repr__(self):
        return f'{self.token}'

class BinaryNode:
    def __init__(self, leftNode, op_token, rightNode):
        self.leftNode = leftNode
        self.op_token = op_token
        self.rightNode = rightNode

        self.pos_start = self.leftNode.pos_start
        self.pos_end = self.rightNode.pos_end

    def __repr__(self):
        return f'({self.leftNode},{self.op_token},{self.rightNode})'

class UnaryNode:
    def __init__(self, op_token, rightNode):
        self.op_token = op_token
        self.rightNode = rightNode

        self.pos_start = op_token.pos_start
        self.pos_end = rightNode.pos_end

    def __repr__(self):
        return f'({self.op_token}, {self.rightNode})'
    
###########
#PARESE RESULT
###########

class ParseResult:
    def __init__(self):
        self.node = None
        self.err = None

#register returns node, if there is err in input, it assigns to parseResult instance
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.err:
                self.err = res.err
            return res.node
        return res
    
    def success(self, node):
        self.node = node
        return self
    
    def failure(self, err):
        self.err = err
        return self
    
###########
#PARSE
###########

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.currentToken = None
        self.index =-1
        self.advance()

    def advance(self):
        self.index += 1
        self.currentToken = self.tokens[self.index] if self.index < len(self.tokens) else None
        return self.currentToken
    
    def factor(self):
        token = self.currentToken
        parseResult = ParseResult()
        if token.tokenType in (TT_INT, TT_FLOAT):
            #advance and return number node obj
            parseResult.register(self.advance())
            return parseResult.success(NumberNode(token))
        if token.tokenType in (TT_PLUS, TT_MINUS):
            #if tokentype is + or - in factor, upcoming expression in unarycode
            parseResult.register(self.advance())
            factor = parseResult.register(self.factor())
            if parseResult.err:
                return parseResult
            return parseResult.success(UnaryNode(token, factor))
        if token.tokenType == TT_LPAREN:
            #if tokentype is left paranthesis, get expression after, check if there is rParen, if not return err
            parseResult.register(self.advance())
            expr = parseResult.register(self.expression())
            if parseResult.err:
                return parseResult
            if self.currentToken.tokenType == TT_RPAREN:
                parseResult.register(self.advance())
                return parseResult.success(expr)
            return parseResult.failure(InvalidSyntaxErr("required ) right paren", self.currentToken.pos_start, self.currentToken.pos_end))
        return parseResult.failure(InvalidCharErr("required int or float", token.pos_start, token.pos_end))


    def expression(self):
        return self.binaryOperation(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.binaryOperation(self.factor, (TT_MUL, TT_DIV))
    
    def binaryOperation(self, func, op_tokens):
        parseResult = ParseResult()
        left = parseResult.register(func())
        if parseResult.err:
            return parseResult
        while(self.currentToken.tokenType in op_tokens):
            op_tok = self.currentToken
            parseResult.register(self.advance())
            right = parseResult.register(func())
            if parseResult.err:
                return parseResult
            left = BinaryNode(left, op_tok, right)
        return parseResult.success(left)

    def parse(self):
        parsedResult = self.expression()
        if not parsedResult.err and self.currentToken.tokenType != TT_EOF:
            return parsedResult.failure(
                InvalidSyntaxErr("required + - * /", self.currentToken.pos_start, self.currentToken.pos_end)
            )
        return parsedResult
    
###########
#RTResult:
###########

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

#whatever that comes here is of instance Number, so instancecheck is not required, we r return value
    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self
    
###########
#VALUES
###########

class Number:

    def __init__(self, tokenValue):
        self.value = tokenValue
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def set_context(self, context = None):
        self.context = context
        return self

    def added_to(self, otherNumber):
        if isinstance(otherNumber, Number):
            return Number(self.value + otherNumber.value).set_context(self.context), None

    def subbed_by(self, otherNumber):
        if isinstance(otherNumber, Number):
            return Number(self.value - otherNumber.value).set_context(self.context), None

    def multed_to(self, otherNumber):
        if isinstance(otherNumber, Number):
            return Number(self.value * otherNumber.value).set_context(self.context), None

    def divided_by(self, otherNumber):
        if isinstance(otherNumber, Number):
            if otherNumber.value == 0:
                return None, RTErr("divided by zero not possible", otherNumber.pos_start, otherNumber.pos_end, self.context)
            return Number(self.value / otherNumber.value).set_context(self.context), None
    
    def __repr__(self):
        return str(self.value)

###########
#CONTEXT
###########

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
    
###########
#INTERPRETER
###########

class Interpreter:

    def visit(self, node, context):
        self.node = node
        typeOfNode = type(node).__name__
        method_name = f'visit_{typeOfNode}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def visit_NumberNode(self, numberNode, context):
        #make the value from numbeNode into numberclass
        return RTResult().success(
            Number(numberNode.token.tokenValue)
            .set_pos(numberNode.pos_start, numberNode.pos_end)
            .set_context(context))

    def visit_BinaryNode(self, binaryNode, context):
        rtResult = RTResult()
        leftNumber = rtResult.register(self.visit(binaryNode.leftNode, context))
        if rtResult.error:
            return rtResult
        rightNumber = rtResult.register(self.visit(binaryNode.rightNode, context))
        if rtResult.error:
            return rtResult
        op_token_type = binaryNode.op_token.tokenType

        binOpResult = Number(0)

        if op_token_type == TT_PLUS:
            binOpResult, error = leftNumber.added_to(rightNumber)
        elif op_token_type == TT_MINUS:
            binOpResult, error = leftNumber.subbed_by(rightNumber)
        elif op_token_type == TT_MUL:
            binOpResult, error = leftNumber.multed_to(rightNumber)
        elif op_token_type == TT_DIV:
            binOpResult, error = leftNumber.divided_by(rightNumber)

        if error:
            return rtResult.failure(error)
        return rtResult.success(
            binOpResult.set_pos(binaryNode.pos_start, binaryNode.pos_end))
        

    def visit_UnaryNode(self, unaryNode, context):
        rtResult = RTResult()
        op_token_type = unaryNode.op_token.tokenType
        rightNumber = rtResult.register(self.visit(unaryNode.rightNode, context))
        if rtResult.error:
            return rtResult

        if op_token_type == TT_MINUS:
            rightNumber, error = rightNumber.multed_to(Number(-1))

        if error:
            return rtResult.failure(error)
        return rtResult.success(
            rightNumber.set_pos(unaryNode.pos_start, unaryNode.pos_end))

    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} is defined')


###########
#RUN
###########

def run(fn, ftxt):
    
    #create lexer
    lexer = Lexer(ftxt, fn)
    tokens, error = lexer.makeTokens()

    if error:
        return None, error
    
    #create Abstract syntax token
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.err:
        return None, ast.err
    
    #calculate, if error, return context
    print(ast.node)
    interpreter = Interpreter()
    context = Context('<program>')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
