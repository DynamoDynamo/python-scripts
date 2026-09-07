#Inspiration from Make YOUR OWN Programming Language - CODEPULSE
import sys
import basic

if len(sys.argv) > 1:
    #then it's file input
    fileName = sys.argv[1]

    with open(fileName, 'r') as fileContent:
        userInput = fileContent.read()

    result, error = basic.run(userInput, fileName)

    if(error):
        print(error)
    else:
        print(result)
else:
    # it's userinput
    while True:

        userInput = input('basic>')

        if userInput.lower() == 'exit':
            sys.exit('see you later!!!')

        result, error = basic.run(userInput, 'file.basic')

        if error:
            print(error)
        else:
            print(result)