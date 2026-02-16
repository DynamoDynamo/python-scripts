
##########
# TOKENS
#########

संख्या = '0123456789'
पूर्णाङ्कः  = 'पूर्णाङ्क:'
दशमिकः = 'दशमिकः'
बिन्दु = '.'

योगः = 'योगः'
वियोगः = 'वियोगः'
गुणनम् = 'गुणनम्'
भागः = 'भागः'
घातः  = 'घातः'

उद्घाटक = 'उद्घाटककोष्टकम्'
समापक = 'समापककोष्टकम्'

अन्तः = 'सन्चिकान्त:'

class Token:
    def __init__(self, प्रकारः, मूल्यम् = None):
        self.प्रकारः = प्रकारः
        self.मूल्यम् = मूल्यम्

    def __repr__(self):
        if self.मूल्यम्:
            return f'{self.प्रकारः}-{self.मूल्यम्}'
        return f'{self.प्रकारः}'
    

##########
#LEXER - tokenizes input
##########

class Lexer:
    def __init__(self, उपयोक्तृनिवेशः):
        self.निवेशः = उपयोक्तृनिवेशः
        self.सूचिका = -1 
        self.वर्तमानाक्षरम् = None
        self.advance()

    def advance(self):
        self.सूचिका += 1 
        self.वर्तमानाक्षरम् = self.निवेशः[self.सूचिका] if self.सूचिका < len( self.निवेशः) else None 

    def makeTokens(self):
        पदानि = []

        while self.वर्तमानाक्षरम् != None:
            if self.वर्तमानाक्षरम् in ' \t':
                self.advance()
            elif self.वर्तमानाक्षरम् == '+':
                पदानि.append(Token(योगः))
                self.advance()
            elif self.वर्तमानाक्षरम् == '-':
                पदानि.append(Token(वियोगः))
                self.advance()
            elif self.वर्तमानाक्षरम् == '*':
                पदानि.append(Token(गुणनम्))
                self.advance()
            elif self.वर्तमानाक्षरम् == '/':
                पदानि.append(Token(भागः))
                self.advance()
            elif self.वर्तमानाक्षरम् == '^':
                पदानि.append(Token(घातः))
                self.advance()
            elif self.वर्तमानाक्षरम् == '(':
                पदानि.append(Token(उद्घाटक))
                self.advance()
            elif self.वर्तमानाक्षरम् == ')':
                पदानि.append(Token(समापक))
                self.advance()
            elif  self.वर्तमानाक्षरम् in संख्या:
                पदानि.append(self.makeNumberTokens())
        पदानि.append(Token(अन्तः))
        return पदानि
    
    def makeNumberTokens(self):
        अक्षरश्रृंखला = ''
        बिन्दुसंख्या = 0 

        while self.वर्तमानाक्षरम्  != None and self.वर्तमानाक्षरम्  in संख्या + बिन्दु:
            if self.वर्तमानाक्षरम् == बिन्दु:
                if बिन्दुसंख्या == 1:
                    break
                बिन्दुसंख्या += 1
            अक्षरश्रृंखला += self.वर्तमानाक्षरम्
            self.advance()

        if बिन्दुसंख्या == 1:
            return Token(दशमिकः, float(अक्षरश्रृंखला))
        return Token(पूर्णाङ्कः, int(अक्षरश्रृंखला))
    
###########
#RUN
###########

def run(उपयोक्तृनिवेशः):
    lexerInstance = Lexer(उपयोक्तृनिवेशः)
    return lexerInstance.makeTokens()



