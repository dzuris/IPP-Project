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

I implemented one extension for the program: **STACK** (closer description [STACK](#STACK))

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
Program for testing `parse.php` and `interpret.py` files

### About

File `test.php` is program for testing programs `parse.php` and `interpret.py`. The program for the first sets 
arguments, format some of them and checks validity. After that the program generates HTML head and styles. Then 
the program gets files by function [getFiles](#getFiles), creates array of tests and cycle through files and transform
the files into tests. After this operation the program has list of Tests with attached files for source, input, output
and return code. Then the program makes another cycle for tests, and it generates missing input and return code files,
and runs tests for parse and interpret according to parse-only and int-only arguments. After tests the program checks
if expected output file and generated output files are same. In this phase the program has all the information about 
tests, so it generates HTML representation for every test. The HTML page is done and printed to stdout and the program
clears the temporary files if no clean argument wasn't passed.

## Functions

Functions used in program:
- **printErrorMessage** - Prints error message and exit with return code which is passed as argument
- **printHelpMessage** - Prints help message for user
- **preStringInArray** - Checks if some element in the array starts with preString
- **[getFiles](#getfiles)** - Get files from directory
- **generateSideBar** - Generate HTML sidebar

### getFiles

The function gets directory name and checks if it exists. Then gets all the files from directory which ends with .src, 
.in, .out or .rc extension. If --recursive argument is passed then the function search all the subdirectories in the 
directory.

## Classes

Classes used in `test.php` program:
- **[Test](#Test)** - Class contains 

### Class Test

#### Variables

Class contains path and name for the test, files with source, input, output and return code. Missing input and return
code file is generated with function generateMissingFiles. Further this class contains file with output generated by
parse and interpret tests, return code generated by these tests and boolean if output files are identical if there
is enough data for comparison. 

#### Functions

Constructor sets name and path from passed string, setFile function sets file by its extension, getId function returns
path name concatenate with file name, getResult returns result of the test according to the return code and expected 
return code and by outputs identity, generateMissingFiles function generates input and return code (with content 0) 
files, parseTest runs test for parser with source file as input and save the file into output file, interpretTest runs
test for interpret with source file from src or output file according to intOnly argument, setOutputsIdentity checks 
differences between output and expected output if it has enough data for comparison, generateFile creates new file with 
passed extension and content and printTest function prints the test data into HTML representation. There are few more
functions for generating HTML elements.

## Program run

Program run as list:
1. Set arguments of the program
2. Generate HTML head and styles for tags
3. Get the files for the tests
4. Transform files into tests
5. Generate missing files for the tests
6. Run parse and interpret tests
7. Set outputs identity
8. Generate HTML sidebar
9. Print tests as HTML representation
10. Clean temporary files according to no clean argument

-----------------------------------------------------------------------------------------------------------------------
## Author

Adam Dzurilla  
xdzuri00