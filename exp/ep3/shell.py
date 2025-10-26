import sys;
import basic;

while True:
    userInput = input('input>')
    if userInput.lower() == 'exit':
        sys.exit()
    result, error = basic.run(userInput, '<sanskrit.in>')
    if result:
        print(result)
    else: 
        print(error)