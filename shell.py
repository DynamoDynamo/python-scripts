
import basic

while True:
    text = input('basic >') #input(variable) takes input from the user
    result, error = basic.run(text)

    if error: print(error.as_string())
    else: print(result)