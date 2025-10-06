import sys
import basic

while True:
    userInput = input('basic>')
    if userInput.lower() == 'exit':
        sys.exit('Bye! Bye! Bye!')
    result, error = basic.run(userInput, 'mockFileName')
    if error:
        print(error)
    else:
        print(result)
