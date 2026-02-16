import sys
import basic
while True:

    userInput = input('basic>')

    if userInput.strip().lower() == 'exit':
        sys.exit("पुन: मिलाम:")

    print(basic.run(userInput))