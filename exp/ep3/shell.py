import sys
import basic

while True:
    userInput = input('<basic> ')
    if userInput.lower() == 'exit':
        sys.exit('bye! see you soon')
    result,error = basic.run(userInput)
    if error:
        print(error)
    else:
        print(result)
    

