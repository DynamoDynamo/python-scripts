from strings_with_arrows import *
import string 


#TASK: Tokenize input
#TASK: Parser - to organize tokens for execution
#TASK: add Error
#TASK: Interpreter - calcualte organized tokens
#TASK: Error for div by zero
#TASK: for variable exressions like >Var a = 5< create tokens

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
DIGITS = "0123456789"
TT_EOF = "EOF"
DOT = "."

TT_KEYWORD = "KEYWORD"
TT_IDENTIFIER = "IDENTIFIER"
TT_EQUAL = "EQUAL"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS
UNDERSCORE = '_'
KEYWORDS = [
    "VAR"
]


class Tokens:
    def __init__(self, tokenType, tokenValue = None, pos_start = None, pos_end = None):
        self.type = tokenType
        self.value = tokenValue
        self.pos_start = pos_start.copy()
        self.pos_end = self.pos_start.copy()
        self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def matches(self, type_, value):
        return self.type == type_ and self.value ==value
        

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

class RunTimeError(Error):
    def __init__(self, errDetails, pos_start, pos_end, context):
        self.context = context
        super().__init__("RunTimeError", errDetails, pos_start, pos_end)

    def __repr__(self):
        errMsg = self.generate_traceback()
        errMsg += f'{self.errorName}:{self.errDetails}\n'
        errMsg += string_with_arrows(self.pos_start.userInput, self.pos_start, self.pos_end)
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
            elif self.currentChar == '=':
                tokens.append(Tokens(TT_EQUAL, pos_start = self.position.copy()))
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
            elif self.currentChar in LETTERS:
                tokens.append(self.makeIdentifierOrKeyWord())
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
    
    def makeIdentifierOrKeyWord(self):
        idt_or_key_str = ''
        pos_start = self.position.copy()
        
        while self.currentChar != None and self.currentChar in LETTERS_DIGITS + UNDERSCORE:
            idt_or_key_str += self.currentChar
            self.advance()

        token_type = TT_KEYWORD if idt_or_key_str in KEYWORDS else TT_IDENTIFIER
        return Tokens(token_type, idt_or_key_str, pos_start=pos_start, pos_end=self.position)
    

###############
#Node
###############

class NumberNode:
    def __init__(self, numToken):
        self.numToken = numToken
        self.pos_start = numToken.pos_start
        self.pos_end = numToken.pos_end

    def __repr__(self):
        return f'{self.numToken}'

class BinaryNode:
    def __init__(self, leftNode, op_tok, rightNode):
        self.leftNode = leftNode
        self.op_tok = op_tok
        self.rightNode = rightNode
        self.pos_start = leftNode.pos_start
        self.pos_end = rightNode.pos_end

    def __repr__(self):
        return f'({self.leftNode},{self.op_tok},{self.rightNode})'
    
class UnaryNode:
    def __init__(self, op_token, rightNode):
        self.op_token = op_token
        self.rightNode = rightNode
        self.pos_start = op_token.pos_start
        self.pos_end = rightNode.pos_end

    def __repr__(self):
        return f'({self.op_token}, {self.rightNode})'
    
class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f'{self.var_name_tok}'

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return  f'({self.var_name_tok}, {self.value_node})'
    
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
        elif currentToken.type == TT_IDENTIFIER:
            self.advance()
            return parseResult.success(VarAccessNode(currentToken))
        elif currentToken.type == TT_LPAREN:
            self.advance()
            expr = parseResult.register(self.expr())
            if parseResult.error:
                return parseResult
            if self.currentToken.type == TT_RPAREN:
                self.advance()
                return parseResult.success(expr)
            else:
                return parseResult.failure(InvalidsyntaxError("'(' Rparen required"), self.currentToken.pos_start, self.currentToken.pos_end)
        else:
            return parseResult.failure(InvalidCharError("required int, float, identifier or math symbol", currentToken.pos_start, currentToken.pos_end))
            
    #Func A is self.atom, meaning it will return number or identifier or expression
    #after funcA, if self.currentToken type is a power, then it will call self. factor(return unary if + or - tokentype)>self.power>returnns self.atom() returns number or identifier or expression
    def power(self):
        return self.bin_op(self.atom, (TT_POW), self.factor)
    
    #By default it will return self.power(), except when currentToken type is + or -, then it will return Unary Number
    def factor(self):
        res = ParseResult()
        tok = self.currentToken
        if tok.type in (TT_PLUS, TT_MINUS):
            self.advance()
            factor = res.register(self.factor())
            if res.error: 
                return res
            return res.success(UnaryNode(tok, factor))
        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))


    def expr(self):
        res = ParseResult()

        if self.currentToken.matches(TT_KEYWORD, 'VAR'):
            res.register(self.advance())

            if self.currentToken.type != TT_IDENTIFIER:
                return res.failure(
                    InvalidsyntaxError(
                        "Expected identifier", 
                        self.currentToken.pos_start, self.currentToken.pos_end
                    )
                )
            identifier_token = self.currentToken
            res.register(self.advance())

            if self.currentToken.type != TT_EQUAL:
                return res.failure(
                    InvalidsyntaxError(
                        "Expected =", self.currentToken.pos_start, self.currentToken.pos_end
                    )
                )
            res.register(self.advance())
            expr = res.register(self.expr())

            if res.error:
                return res
            return res.success(VarAssignNode(identifier_token, expr))

        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, funcA, opTokens, funcB = None):
        if funcB == None:
            funcB = funcA
        parseResult = ParseResult()
        left = parseResult.register(funcA())
        if parseResult.error:
            return parseResult
        while self.currentToken.type in opTokens:
            op_token = self.currentToken
            self.advance()
            right = parseResult.register(funcB())
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
#SYMBOLTABLE
###############

class IdentifierValueTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]

###########
#CONTEXT
###########

class Context:
    def __init__(self, display_name, parent = None, parent_entry_pos = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos  
        self.identifierValue_table = None

###############
#InterpreterResult
###############

class InterpreterResult:

    def __init__(self):
        self.pNumber = None
        self.error = None

    def register(self, resObj):
        if isinstance(resObj, InterpreterResult):
            if resObj.error:
                self.error = resObj.error
            return resObj.pNumber
        return resObj

    def success(self, pNumber):
        self.pNumber = pNumber
        return self

    def failure(self, error):
        self.error = error
        return self
    
###############
#NUMBER
###############

class PNumber:

    def __init__(self, number):
        self.number = number
        self.setContext()

    def __repr__(self):
        return f'{self.number}'

    def setPos(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def setContext(self, context = None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number + other.number).setContext(self.context), None
        
    def sub_by(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number - other.number).setContext(self.context), None
        
    def div_by(self, other):
        if isinstance(other, PNumber):
            if other.number == 0:
                return None, RunTimeError("Division by zero is not possible", other.pos_start, other.pos_end, self.context)
            return PNumber(self.number / other.number).setContext(self.context), None
    
    def multed_to(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number * other.number).setContext(self.context), None
    
    def pow_by(self, other):
        if isinstance(other, PNumber):
            return PNumber(self.number ** other.number).setContext(self.context), None
        
    def copy(self):
        copy = PNumber(self.number)
        copy.setPos(self.pos_start, self.pos_end)
        copy.setContext(self.context)
        return copy

###############
#INTERPRETER
###############

class Interpreter:
    
    def visit(self, node, context):
        typeOfNode = type(node).__name__
        self.methodName = f'visit_{typeOfNode}'
        method = getattr(self, self.methodName, self.no_visit)
        return method(node, context)
    
    def no_visit(self, node, context):
        raise Exception(f'visit_{type(node).__name__} method is not available')
    
    #this method returns PNumber
    def visit_NumberNode(self, node, context):
        return InterpreterResult().success(
            PNumber(node.numToken.value)
            .setPos(node.pos_start, node.pos_end)
            .setContext(context)
            )

    def visit_BinaryNode(self, node, context):
        interpreterResult = InterpreterResult()
        leftNum = interpreterResult.register(self.visit(node.leftNode, context))
        if interpreterResult.error:
            return interpreterResult
        rightNum = interpreterResult.register(self.visit(node.rightNode, context))
        if interpreterResult.error:
            return interpreterResult
        op_token_type = node.op_tok.type

        if op_token_type == TT_MUL:
            resultNum, error = leftNum.multed_to(rightNum)
        elif op_token_type == TT_DIV:
            resultNum,error = leftNum.div_by(rightNum)
        elif op_token_type == TT_POW:
            resultNum, error = leftNum.pow_by(rightNum)
        elif op_token_type == TT_PLUS:
            resultNum, error = leftNum.added_to(rightNum)
        elif op_token_type == TT_MINUS:
            resultNum, error = leftNum.sub_by(rightNum)

        if error:
            return interpreterResult.failure(error)
        else:
            return interpreterResult.success(resultNum.setPos(node.pos_start, node.pos_end))

    def visit_UnaryNode(self, node, context):
        interpreterResult = InterpreterResult()
        rightNum = interpreterResult.register(self.visit(node.rightNode, context))
        if interpreterResult.error:
            return interpreterResult
        op_tok_type = node.op_token.type

        if op_tok_type == TT_MINUS:
            rightNum, error = rightNum.multed_to(PNumber(-1))

        if error:
            return interpreterResult.failure(error)
        return interpreterResult.success(rightNum.setPos(node.pos_start, node.pos_end))
    
    #this method is used to assign Obj of varNames and values to identifierVarTable
    def visit_VarAssignNode(self, node, context):
        interpreterResult = InterpreterResult()
        print(type(node.var_name_tok).__name__)
        print(type(node.value_node).__name__)

        #take the values from node LHS is variable name, RHS can be UnaryNode(-3), NumberNOde(7), BinaryNode((3 + 5) /3) or another variable meaning access node
        var_name = node.var_name_tok.value
        value = interpreterResult.register(self.visit(node.value_node, context))
        if interpreterResult.error:
            return interpreterResult
        
        context.identifierValue_table.set(var_name, value)
        return interpreterResult.success(value)
    
    def visit_VarAccessNode(self, node, context):
        interpreterResult = InterpreterResult()
        #take the values from the node
        var_name = node.var_name_tok.value
        value = context.identifierValue_table.get(var_name)
        if not value:
            return interpreterResult.failure(RunTimeError("variable value is not assigned", node.pos_start, node.pos_end, context))
        value = value.copy().setPos(node.pos_start, node.pos_end)
        return interpreterResult.success(value)




###############
#RUN
###############

global_symbol_table = IdentifierValueTable()
global_symbol_table.set("null", PNumber(0))
    
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

    
    #create context
    context = Context('<programe>')
    context.identifierValue_table = global_symbol_table
    result = interpreter.visit(parseResult.node, context)
    return result.pNumber, result.error

