
import sys;
import basic;

while True:
    #ask input and store in variable
    inputVar = input('basic>')
    if(inputVar.lower() == 'exit'):
        sys.exit("Bye Bye!")
    result, error = basic.run(inputVar)

    if error:
        print(error.as_string())
    else:
        print(result)
    

#STEP1: define tokens for each number and symbol