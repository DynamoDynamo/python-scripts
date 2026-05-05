import sys
import basic

while True:
    #take input
    userInput = input('basic>')
    if(userInput.lower() == 'exit'):
        sys.exit('Out of the Program')
    result, error = basic.run(userInput, '<shell.py>')
    if error:
        print(error)
    else:
        print(result)