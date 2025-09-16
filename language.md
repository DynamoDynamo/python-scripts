# Creating Your Own Programming Language – Telugu Example

## 1️⃣ Core Steps to Make a Programming Language
1. **Define Purpose** – Decide the problem your language will solve.  
2. **Design Syntax & Semantics** – Choose how code looks and what it means.  
3. **Lexer / Tokenizer** – Break code into meaningful tokens (keywords, numbers, operators).  
4. **Parser** – Build an Abstract Syntax Tree (AST) from tokens.  
5. **Interpreter / Compiler** – Execute code (interpreter) or convert to another language/machine code (compiler).  
6. **Standard Library** – Provide built-in functions for common tasks.  
7. **IDE / Tools** – Optional, but helpful for syntax highlighting and debugging.

**Resources:**  
- FreeCodeCamp: Programming language pipeline overview  
- Evan Typanski: Writing a simple language from scratch  
- Robert Nystrom: *Crafting Interpreters*

**Tips:** Start small, iterate, seek feedback, stay persistent.

---

## 2️⃣ Making a Non-English Programming Language
- Keywords and function names can be in any language (Telugu, Hindi, Japanese, etc.).  
- Extra considerations:
  - **Unicode support** for lexer/parser  
  - Keyboard input for local language  
  - IDE/tooling must support the language’s characters  
  - Standard library functions and error messages can also be localized  

---

## 3️⃣ Tiny Telugu-Style Programming Language Example

**Keywords:**  
- `ముద్రించు` → `print`  
- `చేర్చు` → `add`  
- `గుణించు` → `multiply`  

**Python Interpreter Example:**
```python
def execute_telugu_line(line):
    tokens = line.strip().split()
    
    if tokens[0] == "ముద్రించు":
        print(" ".join(tokens[1:]))
    elif tokens[0] == "చేర్చు":
        print(int(tokens[1]) + int(tokens[2]))
    elif tokens[0] == "గుణించు":
        print(int(tokens[1]) * int(tokens[2]))

program = [
    "ముద్రించు హలో ప్రపంచం!",
    "చేర్చు 5 7",
    "గుణించు 3 4"
]

for line in program:
    execute_telugu_line(line)
