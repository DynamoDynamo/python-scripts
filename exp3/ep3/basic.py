
#1. translate mathematical input to tokens
# 1 + 3 - 5 > INT:1 PLUS INT:3 MINUS INT:5
#2. Add Error
#3. Add Pos to Error
#4. Organize tokens

from string_with_arrow import *


###################
#Tokens
###################
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'

DIGITS = '0123456789'
PERIOD = '.'

class Token:
    def __init__(self, tokenType, posStart, tokenValue = None, posEnd = None):
        self.type = tokenType
        self.value = tokenValue
        self.posStart = posStart
        if(posEnd):
            self.posEnd = posEnd
        else:
            self.posEnd = posStart.copy()
            self.posEnd.advance()

    def __repr__(self):
        repr = f'{self.type}'
        if(self.value):
            repr = f'{self.type}:{self.value}'
        return repr

###################
#Error
###################   

class Error:
    def __init__(self, errorType, errorDetails, posStart, posEnd):
        self.errorType = errorType
        self.errorDetails = errorDetails
        self.posStart = posStart
        self.posEnd = posEnd

    def __repr__(self):
        repr = f'{self.errorType}: {self.errorDetails}\n'
        repr += f'File {self.posStart.fileName}, Line {self.posStart.ln + 1}\n'
        repr += string_with_arrows(self.posStart.userInput, self.posStart, self.posEnd)
        return repr

class IllegalCharError(Error):

    def __init__(self, errorDetails, posStart, posEnd):
        super().__init__("Illegal character", errorDetails, posStart, posEnd)

class IllegalSyntaxError(Error):

    def __init__(self, errorDetails, posStart, posEnd):
        super().__init__("Illegal Syntax", errorDetails, posStart, posEnd)

###################
#Position
###################

class Position:
    def __init__(self, ln, col, idx, userInput, fileName):
        self.ln = ln
        self.col = col
        self.idx = idx
        self.userInput = userInput
        self.fileName =  fileName

    def advance(self, currentChar=None):
        self.idx += 1
        if(currentChar == '\n'):
            self.ln += 1
            self.col = 0
        else:
            self.col += 1

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.userInput, self.fileName)
    
###################
#Node
###################

class NumberNode:
    def __init__(self, numberToken):
        self.numberToken = numberToken

    def __repr__(self):
        return f'{self.numberToken}'
    
class BinaryNode:
    def __init__(self, leftNode, rightNode, opToken):
        self.leftNode = leftNode
        self.rightNode = rightNode
        self.opToken = opToken

    def __repr__(self):
        return f'({self.leftNode}, {self.opToken}, {self.rightNode})'
    
class UnaryNode:
    def __init__(self, opToken, rightNode):
        self.opToken = opToken
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.opToken}, {self.rightNode})'
    
###################
#ParseResult - to tie node and error under one class
###################

class ParseResult:
    def __init__(self):
        self.node = None
        self.error = None

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

#regiseter returns node, if there is error in input, it assigns the error to currentParseResultObj
    def register(self, parseInput):
        #if res is not a instance of ParseResult, it must be instance of Token or one of the nodes
        #Ultimately we r returning those nodes or tokens, 
        # if input is instance of parseResult, we r assigning error to the ParseResult and returning node/Token object
        if isinstance(parseInput, ParseResult):
            if parseInput.error:
                self.error = parseInput.error
            return parseInput.node
        return parseInput
    
###################
#Number
###################


class Number:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'
    
    def add_to(self, other):
        if(isinstance(other, Number)):
            return Number(self.value+other)
    def sub_to(self, other):
        if(isinstance(other, Number)):
            return Number(self.value-other)
    def mul_to(self, other):
        if(isinstance(other, Number)):
            return Number(self.value*other)
    def div_by(self, other):
        if(isinstance(other, Number)):
            return Number(self.value/other)

###################
#Interpreter
###################
  
class Interpreter:
    def visit(self, node):
        #we are creating a method name
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, 'no_visit_method')
        return method(node)
    
    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    def visit_NumberNode(self, node):
        print(f'found Number node {node}')

    def visit_BinaryNode(self, node):
        print(f'found Binary node {node.leftNode}:{node.rightNode}')
        self.visit(node.leftNode)
        self.visit(node.rightNode)

    def visit_UnaryNode(self, node):
        print(f'found UnaryNode {node.rightNode}')
        self.visit(node.rightNode)
    
###################
#Parser
###################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIdx = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        self.tokenIdx += 1
        self.currentToken = self.tokens[self.tokenIdx] if self.tokenIdx < len(self.tokens) else None

    def factor(self):
        parseResult = ParseResult()
        token = self.currentToken

        if(token.type in (TT_INT, TT_FLOAT)):
            self.advance()
            return parseResult.success(NumberNode(token))
        elif(token.type == TT_LPAREN):
            self.advance()
            expression = parseResult.register(self.expression())
            if parseResult.error:
                return parseResult
            if(self.currentToken.type == TT_RPAREN):
                self.advance()
                return parseResult.success(expression)
            else:
                return parseResult.failure(
                    IllegalSyntaxError("Expected ')'", self.currentToken.posStart, self.currentToken.posEnd)
                )
        elif(token.type in (TT_PLUS, TT_MINUS)):
            self.advance()
            factorNode = parseResult.register(self.factor())
            if parseResult.error:
                return parseResult
            unaryNode = UnaryNode(token, factorNode)
            return parseResult.success(unaryNode)
        else:
            return parseResult.failure(
                IllegalCharError("Expected number", token.posStart, token.posEnd)
            )
        

    def term(self):
        parseResult = ParseResult()
        leftNode = parseResult.register(self.factor())
        if parseResult.error:
            return parseResult
        while(self.currentToken.type in (TT_MUL, TT_DIV)):
            opToken = self.currentToken
            self.advance()
            rightNode = parseResult.register(self.factor())
            if parseResult.error:
                return parseResult
            leftNode = BinaryNode(leftNode, rightNode, opToken)
        return parseResult.success(leftNode)

    def expression(self):
        parseResult = ParseResult()
        leftNode = parseResult.register(self.term())
        if parseResult.error:
            return parseResult
        while(self.currentToken.type in (TT_PLUS, TT_MINUS)):
            opToken = self.currentToken
            self.advance()
            rightNode = parseResult.register(self.term())
            if parseResult.error:
                return parseResult
            leftNode = BinaryNode(leftNode, rightNode, opToken)
        return parseResult.success(leftNode)

    def parse(self):
        parseResult = self.expression()
        if not parseResult.error and self.currentToken.type != TT_EOF:
            return parseResult.failure(
                IllegalSyntaxError("Expected a math symbol", self.currentToken.posStart, self.currentToken)
            )
        return parseResult

###################
#Lexer - Lexer translate mathematical input tokens
###################

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.index = -1
        self.tokenPos = Position(0, -1, -1, userInput, fileName)
        self.currentChar = None
        self.advance()

    def advance(self):
        self.tokenPos.advance()
        self.currentChar = self.userInput[self.tokenPos.idx] if self.tokenPos.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while(self.currentChar != None):
            if(self.currentChar == '+'):
                tokens.append(Token(TT_PLUS, self.tokenPos))
                self.advance()
            elif(self.currentChar == '-'):
                tokens.append(Token(TT_MINUS, self.tokenPos))
                self.advance()
            elif(self.currentChar == '*'):
                tokens.append(Token(TT_MUL, self.tokenPos))
                self.advance()
            elif(self.currentChar == '/'):
                tokens.append(Token(TT_DIV, self.tokenPos))
                self.advance()
            elif(self.currentChar == '('):
                tokens.append(Token(TT_LPAREN, self.tokenPos))
                self.advance()
            elif(self.currentChar == ')'):
                tokens.append(Token(TT_RPAREN, self.tokenPos))
                self.advance()
            elif(self.currentChar in DIGITS):
                tokens.append(self.makeNumberTokens())
            elif(self.currentChar in ' \t'):
                self.advance()
            else:
                #Return error
                currentChar = self.currentChar
                currentPos = self.tokenPos.copy()
                self.advance()
                return None, IllegalCharError(currentChar, currentPos, self.tokenPos)
        tokens.append(Token(TT_EOF, self.tokenPos))
        return tokens, None

    def makeNumberTokens(self):
        numStr = ''
        periodCount = 0
        startPos = self.tokenPos.copy()
        while(self.currentChar != None and self.currentChar in DIGITS + PERIOD):
            if(self.currentChar == PERIOD):
                if(periodCount == 1):
                    break
                else:
                    periodCount += 1
            numStr += self.currentChar
            self.advance()
        
        if(periodCount == 1):
            return Token(TT_FLOAT, startPos, float(numStr), self.tokenPos)
        else:
            return Token(TT_INT, startPos, int(numStr), self.tokenPos)
    


###################
#Run
###################
def run(userInput, fileName):

    #Generate Tokens
    lexer = Lexer(userInput, fileName)
    tokens, error =  lexer.makeTokens()
    if error:
        return None, error
    
    #Generate Asymetrical Tokens
    parser = Parser(tokens)
    result = parser.parse()
    if result.error:
        return None, result.error
    
    #Run programe
    print('is the node')
    print(result.node)
    interpreter = Interpreter()
    interpreterResult = interpreter.visit(result.node)
    return result.node, None

