import sys
import basic

while True: #create an infinite loop
    userInput = input('basic>') #take user input
    if userInput.lower() == 'exit':
        sys.exit('see you soon!')
    tokens, err = basic.run('<stdin>', userInput)
    if err:
        print(err)
    else:
        print(tokens)