import basic
import sys

while True:
    inputText = input('basic> ')
    if inputText.lower() == 'exit':
        sys.exit('Exit program')
    tokens, errors = basic.run('<stdin', inputText)

    if errors: print(errors.as_string())
    else: print(tokens)
