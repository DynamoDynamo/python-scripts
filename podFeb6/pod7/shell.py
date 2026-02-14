import sys
import basic


while True:
    userInput = input("basic>")

    #exit strategy
    if userInput.lower() == 'exit':
        sys.exit("See you soon")

    print(basic.run(userInput))