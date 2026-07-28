#interactive mode

import sys
import basic

#take input from user and send it to logic file
while True: #create infity loop
    userinput = input('basic>')
    #exit condition
    if userinput.strip().lower() == 'exit':
        sys.exit('bye!')
    result, error = basic.run(userinput)
    if error:
        print(error)
    else:
        print(result)