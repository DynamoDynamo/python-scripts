#TASK: tokenize input

###########
#TOKENS
###########

संख्या  = '0123456789'
बिन्दु = '.'
योगह = 'योग:'
वियोगह = 'वियोग:'
गुणनम् = 'गुणनम्'
भागह = 'भाग:'
उद्घाटक = 'उद्घाटककोष्टकम्'
समापक = 'समापककोष्टकम्'
पूर्णाङ्कह = "पूर्णाङ्क:"
दशमिकह = "दशमिक:" 
घातह = "घात:"


अन्तः = 'सन्चिकान्त'


class संकेतह:
    def __init__(self, प्रकारह, मूल्यम् = None):
        self.प्रकारह = प्रकारह
        self.मूल्यम् = मूल्यम्

    def __repr__(self):
        if self.मूल्यम्:
            return f'{self.प्रकारह}-{self.मूल्यम्}'
        return f'{self.प्रकारह}'
    
########
#LEXER - tokenize
#######

class Lexer:
    def __init__(self, निवेशह):
        self.निवेशह = निवेशह
        self.वर्तमानाक्षरम् = None
        self.सूचिका = -1
        self.advance()

    def advance(self):
        self.सूचिका += 1
        self.वर्तमानाक्षरम् = self.निवेशह[self.सूचिका] if self.सूचिका < len(self.निवेशह) else None

        
    def makeTokens(self):
        पदानि = []

        while self.वर्तमानाक्षरम् != None:
            if self.वर्तमानाक्षरम् in ' \t':
                self.advance()
            elif self.वर्तमानाक्षरम् == '+':
                पदानि.append(संकेतह(योगह))
                self.advance()
            elif self.वर्तमानाक्षरम् == '-':
                पदानि.append(संकेतह(वियोगह))
                self.advance()
            elif self.वर्तमानाक्षरम् == '*':
                पदानि.append(संकेतह(गुणनम्))
                self.advance()
            elif self.वर्तमानाक्षरम् == '/':
                पदानि.append(संकेतह(भागह))
                self.advance()
            elif self.वर्तमानाक्षरम् == '(':
                पदानि.append(संकेतह(उद्घाटक))
                self.advance()
            elif self.वर्तमानाक्षरम् == ')':
                पदानि.append(संकेतह(समापक))
                self.advance()
            elif self.वर्तमानाक्षरम् == '^':
                पदानि.append(संकेतह(घातह))
                self.advance()
            elif self.वर्तमानाक्षरम् in संख्या:
                पदानि.append(self.makeNumberTokens())
        return पदानि
    
    def makeNumberTokens(self):
        अक्षरश्रुंखला  = ''
        बिन्दुसंख्या = 0 

        while self.वर्तमानाक्षरम् != None and self.वर्तमानाक्षरम् in संख्या + बिन्दु:
            if self.वर्तमानाक्षरम् == बिन्दु:
                if बिन्दुसंख्या == 1:
                    break
                बिन्दुसंख्या += 1 
            अक्षरश्रुंखला += self.वर्तमानाक्षरम् 
            self.advance()

        if बिन्दुसंख्या == 1:
            return संकेतह(दशमिकह, float(अक्षरश्रुंखला))
        return संकेतह(पूर्णाङ्कह, int(अक्षरश्रुंखला))
        
###########
# RUN
###########

def run(निवेशह):
    lexer  = Lexer(निवेशह)
    return lexer.makeTokens()

    