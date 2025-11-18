import sys;
import basic;
while True:
    userInput = input("basic>")
    if(userInput.lower() == 'exit'):
        sys.exit("See you soon!")
    result, error = basic.run(userInput, "experiment.sa")
    if(result):
        print(result)
    else:
        print(error)