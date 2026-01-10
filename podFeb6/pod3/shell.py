import sys
import basic

# create an infinite loop
while True:
    # grab user input
    userInput = input('basic>')
    # exit code
    if userInput.lower() == 'exit':
        sys.exit("Bye!")
    result, error = basic.run(userInput, '<stdin>')
    if error:
        print(error)
    else:
        print(result)
