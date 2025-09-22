import sys
import basic

while True:
    #take an input
    userInput = input('<basic>:')
    if(userInput.lower() == 'exit'):
        sys.exit()
    tokens, error = basic.run('STDIN', userInput)
    if tokens == None:
        print(error)
    else:
        print(tokens)

    