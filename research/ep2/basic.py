
##############
#ERROR
###############

from string_with_arrows import string_with_arrows

class Error:
    def __init__(self, errorType, errorDetails, pos_start, pos_end):
        self.type = errorType
        self.details = errorDetails
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        errMsg =  f'{self.type}: {self.details}\n'
        errMsg += f'File: {self.pos_start.fn}, line: {self.pos_start.ln + 1}\n'
        errMsg += string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return errMsg

class IllegalCharacterError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__('IllegalCharacterError', errorDetails, pos_start, pos_end)

class InvalidSyntaxError(Error):
    def __init__(self, errorDetails, pos_start, pos_end):
        super().__init__('InvalidSyntaxError', errorDetails, pos_start, pos_end)
##############
#TOKENS
###############

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'

DIGITS = '0123456789'
DOT = '.'

TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'

TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'

TT_EOF = 'EOF'

class Token:
    def __init__(self, tokenType, tokenValue = None, posStart = None, posEnd = None):
        self.type = tokenType
        self.value = tokenValue

        if posStart:
            self.posStart = posStart.copy()
            self.posEnd = posStart.copy()
            self.posEnd.advance()

        if posEnd:
            self.posEnd = posEnd

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}' #INT:3, FLOAT:3.3
        else:
            return f'{self.type}' #PLUS,MINUS

#####################
# Position
####################

class Position:
    def __init__(self, line, column, index, fileName, fileContent):
        self.ln = line
        self.col = column
        self.idx =index
        self.fn = fileName
        self.ftxt = fileContent

    def advance(self, currentChar = None):
        self.idx += 1
        self.col += 1

        if(currentChar == '\n'):
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.ln, self.col, self.idx, self.fn, self.ftxt)

#####################
# LEXER - to convert useriNput to tokens
####################

class Lexer:
    def __init__(self, userInput, fileName):
        self.userInput = userInput
        self.position = Position(0, -1, -1, fileName, userInput)
        self.currentChar = None
        self.advance()

    def advance(self):
        self.position.advance(self.currentChar)
        self.currentChar = self.userInput[self.position.idx] if self.position.idx < len(self.userInput) else None

    def makeTokens(self):
        tokens = []

        while self.currentChar != None:
            if self.currentChar in ' \t\n':
                self.advance()
            elif self.currentChar == '+':
                tokens.append(Token(TT_PLUS, posStart=self.position))
                self.advance()
            elif self.currentChar == '-':
                tokens.append(Token(TT_MINUS, posStart=self.position))
                self.advance()
            elif self.currentChar == '*':
                tokens.append(Token(TT_MUL, posStart=self.position))
                self.advance()
            elif self.currentChar == '/':
                tokens.append(Token(TT_DIV, posStart=self.position))
                self.advance()
            elif self.currentChar == '(':
                tokens.append(Token(TT_LPAREN, posStart=self.position))
                self.advance()
            elif self.currentChar == ')':
                tokens.append(Token(TT_RPAREN, posStart=self.position))
                self.advance()
            elif self.currentChar in DIGITS:
                tokens.append(self.makeNumberToken())
            else:
                #ERROR SCENARIO
                pos_start = self.position.copy()
                currentChar = self.currentChar
                return None, IllegalCharacterError(currentChar, pos_start, self.position.advance())
        tokens.append(Token(TT_EOF, posStart=self.position))
        return tokens, None

    def makeNumberToken(self):
        numStr = ''
        dot_count = 0
        pos_start = self.position.copy()

        while self.currentChar != None and (self.currentChar in DIGITS or self.currentChar == DOT):
            if self.currentChar == DOT:
                if dot_count == 1:
                    break
                dot_count += 1
            numStr += self.currentChar
            self.advance()

        if dot_count == 1:
            return Token(TT_FLOAT, float(numStr), posStart=pos_start, posEnd=self.position)
        else:
            return Token(TT_INT, int(numStr), posStart=pos_start, posEnd=self.position)
#############
#NODES
###############

class NumberNode:
    def __init__(self, numberToken):
        self.token = numberToken

    def __repr__(self):
        return f'{self.token}'

class BinaryOpNode:
    def __init__(self, leftNode, opToken, rightNode):
        self.leftNode = leftNode
        self.opToken = opToken
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.leftNode} {self.opToken} {self.rightNode})'

class UnaryNode:
    def __init__(self, operatorToken, rightNode):
        self.opToken = operatorToken
        self.rightNode = rightNode

    def __repr__(self):
        return f'({self.opToken} {self.rightNode})'
#############
#PARSE RESULT
###############

class ParseResult:
    def __init__(self):
        self.node = None
        self.error = None

    def registerSuccess(self, node):
        self.node = node
        return self

    def registerFailure(self, error):
        self.error = error
        return self

    def registerErrorAndGetNode(self, nodeOrParseResult):
        if isinstance(nodeOrParseResult, ParseResult):
            if nodeOrParseResult.error:
                self.error = nodeOrParseResult.error
            return nodeOrParseResult.node
        return nodeOrParseResult

#############
#PARSER
###############

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
        parseResultInstance = ParseResult()
        token = self.currentToken
        if(token.type in (TT_INT, TT_FLOAT)):
            self.advance()
            return parseResultInstance.registerSuccess(NumberNode(token))
        elif(token.type in (TT_PLUS, TT_MINUS)):
            self.advance()
            rightNode =  parseResultInstance.registerErrorAndGetNode(self.factor())
            if parseResultInstance.error:
                return parseResultInstance
            return parseResultInstance.registerSuccess(
                UnaryNode(token, rightNode))
        else:
            self.advance()
            return parseResultInstance.registerFailure(
                InvalidSyntaxError("Number missing", token.posStart, token.posEnd))
        

    def term(self):
        return self.binaryOp(self.factor, (TT_MUL, TT_DIV))

    def expression(self):
            return self.binaryOp(self.term, (TT_PLUS, TT_MINUS))

    def binaryOp(self, func, tokenTypes):
        parseResult = ParseResult()
        leftNode = parseResult.registerErrorAndGetNode(func())
        if parseResult.error:
            return parseResult
        while(self.currentToken.type in tokenTypes):
            opToken = self.currentToken
            self.advance()
            rightNode = parseResult.registerErrorAndGetNode(func())
            if parseResult.error:
                return parseResult
            leftNode = BinaryOpNode(leftNode, opToken, rightNode)
        return parseResult.registerSuccess(leftNode)

    def parse(self):
        parseResult = self.expression()
        if not parseResult.error and self.currentToken.type != TT_EOF:
            #math symbol is missing
            parseResult.registerFailure(
                InvalidSyntaxError("Math symbol is missing + - * /", self.currentToken.posStart, self.currentToken.posEnd))
        return parseResult.node, parseResult.error

#############
#RUN
###############

def run(userInput, fileName):
    lexerInstance = Lexer(userInput, fileName)
    tokens, error =  lexerInstance.makeTokens()

    if error:
        return None, error

    parserInstance = Parser(tokens)
    return parserInstance.parse()