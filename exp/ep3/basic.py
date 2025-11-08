from strings_with_arrow import *

###########
#Error
###########
class Error:
    def __init__(self, errorName, errorDetails, pos_start, pos_end):
        self.errorName = errorName
        self.errorDetails = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end
    
    def __repr__(self):
        errorMsg = f'{self.errorName}:{self.errorDetails}\n'
        errorMsg += f'at Line {self.pos_start.ln}, in file{self.pos_start.fn}\n'
        errorMsg += string_with_arrows(self.pos_start.text, self.pos_start, self.pos_end)

        return errorMsg

class IllegalCharError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("Illegal Char", errorDetails, pos_start, pos_end)

class IllegalSyntaxError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__("Illegal syntax", errorDetails, pos_start, pos_end)

###########
#LEXER
###########
class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.tokenPos = Position(-1, 0, -1, userInput, fileName)
        self.currentLetter = None
        self.advance()

    def advance(self):
        self.tokenPos.advance(self.currentLetter)
        self.currentLetter = self.userInput[self.tokenPos.idx] if self.tokenPos.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []
        while (self.currentLetter != None):
            if self.currentLetter in (' \t'):
                self.advance()
            elif self.currentLetter == '+':
                tokens.append(Token(self.tokenPos, TT_PLUS))
                self.advance()
            elif self.currentLetter == '-':
                tokens.append(Token(self.tokenPos, TT_MINUS))
                self.advance()
            elif self.currentLetter == '*':
                tokens.append(Token(self.tokenPos, TT_MUL))
                self.advance()
            elif self.currentLetter == '/':
                tokens.append(Token(self.tokenPos, TT_DIV))
                self.advance()
            elif self.currentLetter == '(':
                tokens.append(Token(self.tokenPos, TT_LPAREN))
                self.advance()
            elif self.currentLetter == ')':
                tokens.append(Token(self.tokenPos, TT_RPAREN))
                self.advance()
            elif self.currentLetter in DIGITS:
                tokens.append(self.makeNumberTokens())
            else:
                #return error
                currentPos = self.tokenPos.copy()
                currentLetter = self.currentLetter
                self.advance()
                return None, IllegalCharError("'"+ currentLetter +"'", currentPos, self.tokenPos)
        tokens.append(Token(self.tokenPos, TT_EOF))
        return tokens, None

    def makeNumberTokens(self):
        numStr = ''
        periodCount = 0
        pos_start = self.tokenPos.copy()

        while self.currentLetter != None and self.currentLetter in DIGITS + PERIOD:
            if(self.currentLetter == PERIOD):
                if(periodCount == 1):
                    break
                else: 
                    periodCount += 1
            numStr += self.currentLetter
            self.advance()
        if(periodCount == 1):
            return Token(pos_start, TT_FLOAT, float(numStr), self.tokenPos)
        else:
            return Token(pos_start, TT_INT, int(numStr), self.tokenPos)

###########
#Parser - to create Abstract Syntax Tokens
###########

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenIndex = -1
        self.currentToken = None
        self.advance()

    def advance(self):
        self.tokenIndex += 1
        self.currentToken = self.tokens[self.tokenIndex] if self.tokenIndex < len(self.tokens) else None

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
            if self.currentToken.type == TT_RPAREN:
                self.advance()
                return parseResult.success(expression)
            else:
                return parseResult.failure(
                    IllegalSyntaxError("Missing ')' right paranthesis", token.pos_start, token.pos_end)
                )
        elif token.type in (TT_PLUS, TT_MINUS):
            self.advance()
            factor = parseResult.register(self.factor())
            if parseResult.error:
                return parseResult
            return parseResult.success(UnaryNode(token, factor))
        else:
            return parseResult.failure(
                IllegalSyntaxError("Missing mathSymbol or number", token.pos_start, token.pos_end)
            )
        
    def term(self):
        parseResult = ParseResult()
        #What object is returned here? one of the nodes or None if error
        #that's why we should deal with parseResult, while checking the errors
        leftNode = parseResult.register(self.factor())
        if parseResult.error:
            return parseResult
        while(self.currentToken.type in (TT_MUL, TT_DIV)):
            opToken = self.currentToken
            self.advance()
            rightNode = parseResult.register(self.factor())
            if parseResult.error:
                return parseResult
            leftNode = BinaryNode(leftNode, opToken, rightNode)
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
            leftNode = BinaryNode(leftNode, opToken, rightNode)
        return parseResult.success(leftNode)
    
    def parse(self):
        result = self.expression()
        if not result.error and self.currentToken.type != TT_EOF:
            return None, IllegalSyntaxError("Missing one of the math symol", self.currentToken.pos_start, self.currentToken.pos_end)
        return result.node, result.error
    
###########
#ParseResult
###########

# result from self.factor(), self.expression(), self.term() is registered in the next methods
#why?
# if there is error, error can be return immediately

class ParseResult:

    def __init__(self):
        self.node = None
        self.error = None

    def register(self, input):
        #if res is not a instance of ParseResult, it must be instance of Token or one of the nodes
        #Ultimately we r returning those nodes or tokens, 
        # if input is instance of parseResult, we r assigning error to the ParseResult and returning node/Token object
        if(isinstance(input, ParseResult)):
            if input.error: 
                self.error = input.error
            return input.node
        return input

    def success(self, node):
        self.node = node
        return self 
    
    def failure(self, error):
        self.error = error
        return self

###########
#Nodes
###########

class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'

class BinaryNode:
    def __init__(self, leftNode, opToken, rightNode):
        self.leftNode = leftNode
        self.opToken = opToken
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.leftNode},{self.opToken},{self.rightNode})'

class UnaryNode:
    def __init__(self, opToken, rightNode):
        self.opToken = opToken
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.opToken},{self.rightNode})'

###########
#TOKEN
###########
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_EOF = 'EOF'
DIGITS = '0123456789'
PERIOD = '.'

class Token:
    def __init__(self,pos_start, tokenType, tokenValue = None, pos_end = None):
        self.type = tokenType
        self.value = tokenValue
        self.pos_start = pos_start.copy()
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
###########
#POSITION
###########

class Position:
    def __init__(self, col, row, index, userInput, fileName):
        self.col = col
        self.ln = row
        self.idx = index
        self.text = userInput
        self.fn = fileName

    def advance(self, currentLetter=None):
        self.idx += 1
        if(currentLetter == '\n'):
            self.col = 0
            self.ln += 1
        else:
            self.col += 1
    def __repr__(self):
        return f'idx{self.idx}:col{self.col}:ln{self.ln}'

    def copy(self):
        return Position(self.col, self.ln, self.idx, self.text, self.fn)

###########
#RUN
###########

def run(userInput, fileName):
    lexer = Lexer(userInput, fileName)
    tokens, error =  lexer.makeTokens()
    if error: return None, error
    parser = Parser(tokens)
    return parser.parse()