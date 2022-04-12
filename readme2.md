Implementační dokumentace k 2. úloze do IPP 2021/2022  
Jméno a příjmení: Adam Dzurilla  
Login: xdzuri00

-----------------------------------------------------------------------------------------------------------------------
# Interpreter

File: `interpret.py`  
Program for interpreting XML file

### About

The program gets the xml file in source_file which is assigned by parameter --source or if this parameter is not 
assigned then source_file is read from standard input. The program processes instructions in the xml file one by one 
and can jump between them. The program recognizes certain errors and based on them prints error messages and exits 
the program with appropriate return code. For running the program uses some classes 
(closer description [Classes](#Classes)). At first the program loads the arguments and remove 
the first one `interpret.py`. Then starts function for checking these arguments. That function recognizes invalid 
arguments combination and return source file and read input files separated into lines. Then program loads xml file 
assigned in source_fil. Loads of the xml file as xml tree is proceeded by library `xml.etree.ElementTree`. The program 
catches errors when it's opening source_file. Then the program creates instantiation of class `Program` which is main 
class of the program. The Program class contains various variables and functions for working with xml 
file (closer description [Program class](#Program-class)). After creating Program class, the program loads the 
instructions from the loaded xml tree into Program class. When everything is loaded program starts iterate (closer 
description [Program iteration](#Program-iteration)).

I implemented one extension for the program: STACK (closer description [STACK](#STACK))

## Classes

The program uses various classes for interpretation, the classes:
- **Type** - Enum class contains valid types which are assigned to the variables
- **Label** - Code representation of the _LABELS_ instructions
- **Instruction** - Code representation of the _instructions_ in code 
- **Argument** - Code representation of the _arguments_ of the xml instructions
- **Variable** - The argument's transformation is stored in Variable with more specific determination and more 
functions for work
- **Frame** - List of undefined type and functions for working with that frame
- **Frames** - The structure of global frame, temporary frame and list of the local frames and functions 
for working with them
- **Stack** - Stack of undefined type, adding variables to the stack is by PUSH and getting variables from stack 
is by POP functions
- [**Program**](#Program-class) - Main class of the program

### Program class

Main class of the program contains variables for program iteration, number of proceeded functions, lists for 
instructions and labels, stacks for variables and calls, frames, input lines and functions for program interpretation.
Program performs functions by own functions which are called by their opcode from function `call_function`. Further, 
contains more functions for working with labels, instructions, arguments, frames, variables and functions for checking 
if program ended iterations and function for comparing arguments.

## Program iteration

### Loading instructions
At the beginning program loads instructions into list. When the program is loading instructions, it's checking their 
order validity (can't be duplicate or negative number). Then sort instructions by their order and rewrite their
orders from one and every order of the every next instruction is incremented by one.

### Calling instructions
Program iteration starts at position zero (Instruction with order 1). Instructions are performed by order number 
one by one in order, only call, return and jump functions can change the iteration number in another way (by jump). 
When program reaches the end of the instructions, the iteration is over, and it's ended with return 
code 0 (if everything ended without error).

### Errors
When program is running functions are build in way that they can recognize errors and when error occurs, the function
prints error message and exit program with return code of the error.

## Extensions

### STACK

Program can process stack functions. Stack functions gets operands from the stack from the last to the first. Makes the operations
and then push result value back on the stack. Extension is implemented in [program class](#Program-class) as
functions. Functions don't get arguments except of jump functions.

-----------------------------------------------------------------------------------------------------------------------
# Test

File: `test.php`  
Program for testing

-----------------------------------------------------------------------------------------------------------------------
## Author

Adam Dzurilla  
xdzuri00