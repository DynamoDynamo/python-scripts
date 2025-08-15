
import basic
import sys

while True:
    text = input('basic >') #input(variable) takes input from the user
    if text.lower() == 'exit':
        sys.exit("Exiting program.")
    result, error = basic.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(result)