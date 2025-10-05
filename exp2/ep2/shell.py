import basic
import sys

while True:
    text = input('basic > ')
    if text.lower() == 'exit':
        sys.exit()
    node, error = basic.run('<stdin>', text)
    if error:
        print(error.as_string())
    else:
        print(node)