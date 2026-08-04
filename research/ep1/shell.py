
import sys
import basic

if len(sys.argv) > 1: #sys.argv collects the list of arguments
    # File mode
    filename = sys.argv[1]

    with open(filename, 'r') as file:
        userinput = file.read()

    result, error = basic.run(userinput, filename)

    if error:
        print(error)
    else:
        print(result)

else:
    # Interactive mode
    while True:
        userinput = input('basic>')

        if userinput.strip().lower() == 'exit':
            sys.exit('bye!')

        result, error = basic.run(userinput, 'userInput.basic')

        if error:
            print(error)
        else:
            print(result)