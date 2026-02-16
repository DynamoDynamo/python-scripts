import sys
import basic


while True:
    userInput = input("basic>")

    #exit strategy
    if userInput.lower() == 'exit':
        sys.exit("See you soon")

    result, error = basic.run(userInput, 'Sanskrit.ba')
    if error:
        print(error)
    else:
        print(result)