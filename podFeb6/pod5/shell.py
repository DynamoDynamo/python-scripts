import sys
import basic

#create infinite loop

while True:
    # ask for input
    userinput = input("basic>")
    if userinput.lower() == 'exit':
        sys.exit("see you soon!")
    tokens, error = basic.run(userinput, 'sanskrit.in')

    if error:
        print(error)
    else:
        print(tokens)