import sys
import basic

#create infinite loop
while True:
    #take userInput
    userInput = input("basic>")

    #exit strategy
    if userInput.lower() == 'exit':
        sys.exit('see you soon !!!')

    #run programe
    tokens, error = basic.run('<stdin>', userInput)

    if error:
        print(error)
    else:
        print(tokens)