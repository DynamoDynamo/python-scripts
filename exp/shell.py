import basic
import sys

while True:
    inputText = input('basic> ')
    if inputText.lower() == 'exit':
        sys.exit('Exit program')
    print(basic.run('<stdin', inputText))
