import sys
import basic

while True:
    userInput = input('input>')
    if userInput.lower() == 'exit':
        sys.exit("see you soon!")
    result, error = basic.run(userInput, '<include>')
    if result:
        print(result)
    if error:
        print(error)