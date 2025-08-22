#######################################
# IMPORTS
#######################################

from string_with_arrows import *

###################################
#CONSTANTS
###################################

DIGITS = '0123456789'

###################################
#ERROR
###################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details): #takes in errorname, details and creates related vars
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

###################################
#POSITION
###################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def __repr__(self):
        return f'index: {self.idx}\nline: {self.ln}\ncolumn: {self.col}\nfileName: {self.fn}\ntext: {self.ftxt}'
    
    def advanced(self, current_char=None):
        ## increment col and idx
        self.idx += 1
        self.col += 1

        #If current_char is new line, go to next line and set col to zero
        if(current_char == '\n'):
            self.ln += 1
            self.col = 0
        
        return self
    
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


###################################
#TOKENS
###################################

TT_INT    = 'INT'
TT_FLOAT  = 'FLOAT'
TT_PLUS   = 'PLUS'
TT_MINUS  = 'MINUS'
TT_MUL    = 'MUL'
TT_DIV    = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF    = 'EOF'

class Token:  #class methods end with :, instead of {}
    def __init__(self, type_, value=None, pos_start=None, pos_end=None): #__iniit__  is default constructor used to initialize values
        self.type = type_ #self is the instance itself, type_ is input, type is var in basic.py
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advanced()

        if pos_end:
            self.pos_end = pos_end
    
    def __repr__(self):   #another dunder method that defines string representation of object
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    
###################################
#LEXER
###################################

class Lexer:   #class to process the text
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        #position will start at index -1, row = 0, col = -1
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advanced()

    def advanced(self):
        self.pos.advanced(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None #if pos<length of text assign current char = text[pos] else None

    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':   # if char is space or a tab, ignore and advance position
                self.advanced()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advanced()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advanced()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advanced()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advanced()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advanced()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advanced()
            else:
                # return error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advanced()
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
            self.advanced()
        
        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
        
###################################
#NODES
###################################

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__(self):
        return f'{self.tok}'
    
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

###################################
#PARSE RESULT
###################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def __repr__(self):
        return f'{self.node}: {self.error}'

#all register is doing is assigning error if input is ParseResult
#if input is not parseResult returning whatever the input is
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self 

###################################
#PARSER
###################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens): # if tok_idx < length of tokens
            self.current_tok = self.tokens[self.tok_idx] # then return tokens[tok_idx]
        return self.current_tok
    
    def parse(self):
        res = self.expr()
        print('final res')
        print(res)
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '+', '-', '*', or '/'"
                )
            )
        return res
    
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        return res.failure(
            InvalidSyntaxError(
                tok.pos_start, tok.pos_end, "Expected int or float"
            )
        )
        
    def term(self):
        term =  self.bin_op(self.factor, (TT_MUL, TT_DIV))
        return term

    def expr(self):
        expression = self.bin_op(self.term, (TT_PLUS, TT_MINUS))
        return expression

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        print('left and funct')
        print(left)
        print(ops)
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)


###################################
#RUN
###################################

def run(fn, text):
    #generates tokens
    lexer = Lexer(fn, text)   # Lexer is initialized
    tokens, error = lexer.make_tokens()
    if error: return None, error

    #generates AST
    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error