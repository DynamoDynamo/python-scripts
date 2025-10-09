from string_with_arrows import *;


#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        self.context = context
        super().__init__(pos_start, pos_end, 'Runtime error', details)

    def as_string(self):
        result = self.generate_traceback()
        result  = f'{self.error_name}: {self.details}\n'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result
    
    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Traceback (most recent call last):\n' + result

#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def __repr__(self):
        return f'{self.idx}:{self.ln}:{self.col}'

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_EOF      = 'EOF'

class Token:
    def __init__(self, type_, value=None, pos_start = None, pos_end = None):
        self.type = type_
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

#######################################
# Nodes
#######################################

class NumberNode:
    def __init__(self, token):
        self.token = token

        self.pos_start = self.token.pos_start
        self.pos_end = self.token.pos_end

    def __repr__(self):
        return f'{self.token}'

class BinaryOpNode:
    #this is not exactly token, it can be node also
    def __init__(self, left_token, op_token, right_token):
        self.left_token = left_token
        self.op_token = op_token
        self.right_token = right_token

        self.pos_start = self.left_token.pos_start
        self.pos_end = self.right_token.pos_end

    def __repr__(self):
        return f'({self.left_token}, {self.op_token}, {self.right_token})'
    
class UnaryOpNode:
    def __init__(self, opToken, node):
        self.opToken = opToken
        self.node = node

        self.pos_start = self.opToken.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f'({self.opToken}, {self.node})'
    

#######################################
# ParseResult
#######################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

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
    
#######################################
# Parser - to build Abstract Syntax Tree out of Tokens
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = -1
        self.advance()

    def advance(self):
        self.tokenIndex += 1
        if self.tokenIndex < len(self.tokens):
            self.currentToken = self.tokens[self.tokenIndex]
        return self.currentToken
    
    def factor(self):
        res = ParseResult()
        token = self.currentToken

        if token.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(token, factor))
        elif token.type in (TT_INT, TT_FLOAT):
            # self.advance() returns TokenObj, If not ParseResultObj res.register() returns the same, and this return value is stored no where
            res.register(self.advance())  
            # returning parseResult Obj
            return res.success(NumberNode(token))
        elif token.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expression())
            if res.error:
                return res
            if self.currentToken.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else: return res.failure(InvalidSyntaxError(token.pos_start, token.pos_end, "Expected ')'"))
        return res.failure(InvalidSyntaxError(token.pos_start, token.pos_end, "Expected int or float"))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))
            

    def expression(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    
    def bin_op(self, func, ops):
        res = ParseResult()
        #left here is parseResult obj, func() also returns parseResultObj
        left = res.register(func())
        if res.error:
            return res

        while self.currentToken.type in ops:
            opToken = self.currentToken
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinaryOpNode(left, opToken,right)
        return res.success(left)

    
    def parse(self):
        res = self.expression()
        if not res.error and self.currentToken.type != TT_EOF:
            return res.failure(InvalidSyntaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected + - * /"))
        return res
    
#######################################
# RUNTIME RESULT
#######################################
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, result):
        if result.error: self.error = result.error
        return result.value
    
    def success(self,value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self


#######################################
# VALUES - to extract numbers and operate on them
# storing the position to show error on which number
#######################################

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def __repr__(self):
        return str(self.value)
    
    def set_context(self, context = None):
        self.context = context
        return self

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        
    def subbed_to(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        
    def multed_to(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        
    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, 'Division by zero', self.context
                )
            return Number(self.value / other.value).set_context(self.context), None
        

    
#######################################
# CONTEXT
#######################################

class Context:
    def __init__(self, display_name, parent = None, parent_entry_pos = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos

#######################################
# Interpreter - looks at parser and determine what code to execute
# if it comes across BinaryNode, it executes left and right token
#######################################

class Interpreter:
    def visit(self, node, context):
        #so type gives the Object type
        #__name__ converts that type to string
        # x = 5, type(x) is int, type(x).__name__ is 'int'
        method_name = f'visit_{type(node).__name__}'
        # getattr method in python takes in (object, attributeName, defaultValue)
        # It's a default method in python
        # so to explain line 304 
        # from object self i:e Interpreter, there is a variable name called method_name, give it's value 
        # if value is not there, provide default value self.no_visit_method
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)
    
    def no_visit_method(self, node, context):
        #in pythong raise is always used for exception
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinaryOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_token, context))
        if res.error: return res
        right = res.register(self.visit(node.right_token, context))
        if res.error: return res

        error = None
        if node.op_token.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_token.type == TT_MINUS:
            result, error = left.subbed_to(right)
        elif node.op_token.type == TT_MUL:
            result, error = left.multed_to(right)
        elif node.op_token.type == TT_DIV:
            result, error = left.divided_by(right)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
        error = None
        if node.opToken.type == TT_MINUS:
            number, error = number.multed_to(Number(-1))
        if error:
            return res.failure(error)
        else: 
            return res.success(number.set_pos(node.pos_start, node.pos_end))




#######################################
# RUN
#######################################

def run(fn, text):
    #generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    
    #generate ast
    parser = Parser(tokens)
    abstractSyntaxTree = parser.parse()
    if abstractSyntaxTree.error:
        return None, abstractSyntaxTree.error
    
    #Run program
    interpreter = Interpreter()
    context = Context('<programe>')
    print(abstractSyntaxTree.node)
    result = interpreter.visit(abstractSyntaxTree.node, context)
    return result.value, result.error