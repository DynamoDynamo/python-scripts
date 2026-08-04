#Inspiration from Make YOUR OWN Programming Language - CODEPULSE
import sys
import basic
while True:

    userInput = input('basic>')

    if userInput.lower() == 'exit':
        sys.exit('see you later!!!')

    result, error = basic.run(userInput)

    if error:
        print(error)
    else:
        print(result)