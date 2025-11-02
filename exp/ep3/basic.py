from strings_with_arrow import *
################
#ERROR
###############

class Error:
    def __init__(self, pos_start, pos_end, errorName, errorDetails):
        self.errorName = errorName
        self.errorDetails = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errorMsg = f'{self.errorName}:{self.errorDetails}\n'
        errorMsg += f'Line {self.pos_start.ln}, File {self.pos_start.fn}\n'
        errorMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)

        return errorMsg

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, errorDetails):
        super().__init__(pos_start, pos_end, "Illegal Character error", errorDetails)

class InvalidSytaxError(Error):
    def __init__(self, pos_start, pos_end, errorDetails):
        super().__init__(pos_start, pos_end, "Invalid Syntax error", errorDetails)

################
#TOKENS
###############
TT_FLOAT = 'FLOAT'
TT_INT = 'INT'
TT_EOF = 'EOF'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
DIGITS = '0123456789'
DOT = '.'

class Token:
    def __init__(self,pos_start, tokenType, tokenValue = None,  pos_end = None):
        self.type = tokenType
        self.value = tokenValue
        self.pos_start = pos_start
        if pos_end != None:
            self.pos_end = pos_end
        else:
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

    def __repr__(self):
        if self.value != None:
            return f'{self.type}:{self.value}'
        else:
            return f'{self.type}'
################
#POSITION
###############

class Position:
    def __init__(self, idx, col, ln, fn, ftxt):
        self.idx = idx
        self.col = col
        self.ln = ln
        self.fn = fn
        self.ftxt = ftxt
    
    def advance(self, currentChar = None):
        self.idx += 1
        if currentChar == '\n':
            self.ln += 1
            self.col = 0
        else:
            self.col += 1
    
    def copy(self):
        return Position(self.idx, self.col, self.ln, self.fn, self.ftxt)
    
################
#LEXER - lexer makes tokens
###############

class Lexer:
    def __init__(self, fileName, userInput):
        self.fileName = fileName
        self.userInput = userInput
        self.currentChar = None
        self.tokenPos = Position(-1, -1, 0, fileName, userInput)
        self.advance()
    
    def advance(self):
        self.tokenPos.advance()
        self.currentChar = self.userInput[self.tokenPos.idx] if self.tokenPos.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(self.tokenPos, TT_PLUS))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(self.tokenPos, TT_MINUS))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(self.tokenPos, TT_MUL))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(self.tokenPos, TT_DIV))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberTokens())
            elif self.currentChar == '(':
                tokens.append(Token(self.tokenPos, TT_LPAREN))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(self.tokenPos, TT_RPAREN))
                self.advance()
            else:
                currentPos = self.tokenPos.copy()
                currentChar = self.currentChar
                self.advance()
                return None, IllegalCharError(currentPos, self.tokenPos, "'" + currentChar + "'")
        tokens.append(Token(self.tokenPos, TT_EOF))
        return tokens, None
        
        
    def makeNumberTokens(self):
        numStr = ''
        dotCount = 0
        while self.currentChar != None and self.currentChar in DIGITS + DOT:
            if self.currentChar == DOT:
                if dotCount == 1:
                    break
                else:
                    dotCount += 1
            numStr += self.currentChar
            self.advance()
        if dotCount == 1:
            return Token(self.tokenPos, TT_FLOAT, float(numStr))
        else:
            return Token(self.tokenPos, TT_INT, int(numStr))
        
################
#NODES
###############

class NumberNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self):
        return f'{self.token}'

class BinaryNode:
    def __init__(self, leftNode, rightNode, opToken):
        self.leftNode = leftNode
        self.rightNode = rightNode
        self.opToken = opToken

    def __repr__(self):
        return f'({self.leftNode}, {self.opToken}, {self.rightNode})'
    
class UnaryNode:
    def __init__(self, opToken, node):
        self.opToken = opToken
        self.node = node

    def __repr__(self):
        return f'({self.opToken}, {self.node})'
        
################
#PARSER - create AbstractSyntaxTokens -oranize the tokens
###############

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.currentToken = None
        self.tokenIndex = -1
        self.advanceToken()

    def advanceToken(self):
        self.tokenIndex += 1
        self.currentToken = self.tokens[self.tokenIndex] if self.tokenIndex < len(self.tokens) else None

    def factor(self):
        parseResult = ParseResult()
        token = self.currentToken
        if(token.type in (TT_INT, TT_FLOAT)):
            self.advanceToken()
            return parseResult.success(NumberNode(token))
        elif(token.type in (TT_MINUS, TT_PLUS)):
            self.advanceToken()
            factor = parseResult.register(self.factor())
            return parseResult.success(UnaryNode(token, factor))
        elif(token.type in (TT_LPAREN, TT_RPAREN)):
            self.advanceToken()
            expression = parseResult.register(self.expression())
            if(self.currentToken.type == TT_RPAREN):
                self.advanceToken()
                return parseResult.success(expression)
            else:
                return parseResult.failure(InvalidSytaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected ')'"))
        return parseResult.failure(InvalidSytaxError(token.pos_start, token.pos_end, "Expected int or float"))
        
    def term(self):
        parseResult = ParseResult()
        left = parseResult.register(self.factor())
        if parseResult.error: 
            return parseResult
        while(self.currentToken.type in (TT_MUL, TT_DIV)):
            opToken = self.currentToken
            self.advanceToken()
            right = parseResult.register(self.factor())
            if parseResult.error:
                return parseResult
            left = BinaryNode(left, right, opToken)
        return parseResult.success(left)

    def expression(self):
        parseResult = ParseResult()
        left = parseResult.register(self.term())
        if parseResult.error:
            return parseResult
        while(self.currentToken.type in (TT_PLUS, TT_MINUS)):
            opToken = self.currentToken
            self.advanceToken()
            right = parseResult.register(self.term())
            if parseResult.error:
                return parseResult
            left = BinaryNode(left, right, opToken)
        return parseResult.success(left)

    def parse(self):
        result =  self.expression()
        if not result.error and self.currentToken.type != TT_EOF:
            return result.failure(
                InvalidSytaxError(self.currentToken.pos_start, self.currentToken.pos_end, "Expected '+', '-', '*', '/'")
            )
        return result

################
#ParseResult - return object from Parser
###############

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if(isinstance(res, ParseResult)):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self
    
    def failure(self, error):
        self.error = error
        return self

################
#RUN
###############
def run(userInput, fileName):
    lexer = Lexer(fileName, userInput)
    tokens, error = lexer.makeTokens()
    if error: return None, error
    print(tokens)
    parser = Parser(tokens)
    ast = parser.parse()
    return ast.node, ast.error
