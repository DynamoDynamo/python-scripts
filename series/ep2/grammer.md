### Rules

**Rule 1:** Multiplication and division have higher precedence.

**Rule 2:** Addition and subtraction have lower precedence.

**Rule 3:** Operators with the same precedence are handled from left to right.

### Parser

The Parser takes the tokens from the Lexer and, 
by applying the above rules, 
determines how the mathematical input is structured and 
which operations have higher priority.

The Parser 
**only gives structure to the input. It does not actually calculate the input.** 
The calculation is the job of the Interpreter.

```
3 + 5 * 7 = 3 + (5 * 7)

    +
   / \
  3   *
     / \
    5   7


3 + 5 * 7 - 8 / 5 
 3 + (5 * 7) - (8 / 5)  
    (3 + (5 * 7)) - (8 / 5)

       -
      / \
     +   /
    / \ / \
   3  * 8  5
     / \
    5   7
```

**Factor:** - A basic elment such as number  
**Term:** -  Factors combined using multiplication or division operator   
**Expression:** -  Terms combined using addition or subtraction operators, forming the complete mathematical input.

```
FACTOR ( * / ) FACTOR  →  TERM
TERM ( + - )  TERM  →  EXPRESSION
````

**Example:** 3 + 5 * 7 = 3 + (5 * 7)  
3, 5, 7 are factors  
5 * 7 is a term  
3 is both factor and a term  
3 + (5 * 7) is a valid expression  

**Example:** 3 + 7  
3, 7 are both terms and factors  
3 + 7 is a valid expression 

