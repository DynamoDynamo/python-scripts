import sys
import basic

#generate infinite loop
while True:
    #take input
    userInput = input("basic>")
    if userInput.lower() == 'exit':
        sys.exit('see you goodbye!')
    result, error = basic.run(userInput, 'Sanskrit.in')
    if error:
        print(error)
    else:
        print(result)