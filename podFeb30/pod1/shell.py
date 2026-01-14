import basic
import sys

while True:
    text = input('basic >')
    if text.lower() == 'exit':
        sys.exit(" bye! ")
    tokens, error = basic.run('<stdin>', text)
    if tokens:
        print(tokens)
    else:
        print(error.as_string())