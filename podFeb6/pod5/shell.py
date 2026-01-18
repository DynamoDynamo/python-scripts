
import sys
import basic

#create infinite loop 

while True:
    #take user input
    userInput = input("basic>")
    #exit strategy
    if userInput.lower() == 'exit':
        sys.exit("See you soon")
    result, error = basic.run(userInput, '<sanskrit.in>')
    if error:
        print(error)
    else:
        print(result)