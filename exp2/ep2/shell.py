import basic
import sys

while True:
    text = input('basic > ')
    if text.lower() == 'exit':
        sys.exit()
    result = basic.run('<stdin>', text)

    print(result)