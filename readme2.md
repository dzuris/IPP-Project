Implementační dokumentace k 2. úloze do IPP 2021/2022  
Jméno a příjmení: Adam Dzurilla  
Login: xdzuri00

-----------------------------------------------------------------------------------------------------------------------
# Interpreter

File: `interpret.py`  
Program for interpreting XML file

### About

The program gets the XML file as source_file assigned by parameter --source. If the parameter is not
assigned the source_file is read from standard input. The program processes instructions in the XML file with the 
ability to jump between them. The program recognizes certain errors and based on them, prints error messages and exits
the program with the appropriate return code. For running, the program uses some classes
(closer description [Classes](#Classes)). At first, the program loads the arguments and removes
the first one `interpret.py`. Then starts a function for checking these arguments. That function recognizes invalid
arguments combination and return source file and read input files separated into lines. Then program loads the XML file
assigned in source_fil. Loads of the XML file as XML tree is preceded by library `xml.etree.ElementTree`. The program
catches errors when it's opening source_file. Then the program creates an instantiation of class `Program` that is the main
class of the program. The Program class contains various variables and functions for working with XML
file (closer description [Program class](#Program-class)). After creating the Program class, the program loads the
instructions from the loaded XML tree into the Program class. When everything is loaded program starts iterate (closer
description [Program iteration](#Program-iteration)).

I implemented one extension for the program: **STACK** (closer description [STACK](#STACK))

## Classes

The program uses various classes for interpretation, the classes:
- **Type** - Enum class contains valid types assigned to the variables
- **Label** - Code representation of the _LABELS_ instructions
- **Instruction** - Code representation of the _instructions_ in code
- **Argument** - Code representation of the _arguments_ of the XML instructions
- **Variable** - The argument's transformation is stored in Variable with more specific determination and more
  functions for work
- **Frame** - List of undefined types and functions for working with that frame
- **Frames** - The structure of the global frame, temporary frame, and list of the local frames and functions
  for working with them
- **Stack** - Stack of an undefined type, adding variables to the stack is by PUSH and getting variables from the stack
  is by POP functions
- [**Program**](#Program-class) - Main class of the program

### Program class

The main class of the program contains variables for program iteration, number of proceeded functions, lists for
instructions and labels, stacks for variables and calls, frames, input lines, and functions for program interpretation.
The program performs functions by its functions that are called by their opcode from function `call_function`. Further,
contains more functions for working with labels, instructions, arguments, frames, variables, and functions for checking
if the program ended iterations and functions for comparing arguments.

## Program iteration

### Loading instructions
In the beginning, the program loads instructions into a list. When the program is loading instructions, it's checking their
order validity (can't be duplicated or negative number). Then sort instructions by their order and rewrite their
orders from one. Every order of every following instruction is incremented by one.

### Calling instructions
Program iteration starts at position zero (Instruction with order 1). Instructions are executed by order number
one by one. Only call, return and jump functions can change the iteration number with one another way (by jump).
When the program reaches the end of the instructions, the iteration is over, and it's ended with the return
code 0 (if everything ended without error).

### Errors
When the program is running, functions are a built-in way that can recognize errors. When an error occurs, the function
prints error message and exit program with return code of the error.

## Extensions

### STACK

The program can process stack functions. Stack functions get operands from the stack from the last to the first. Makes the operations
and then push the result value back on the stack. Extension is implemented in [program class](#Program-class) as
functions. Functions don't get arguments except for jump functions.

-----------------------------------------------------------------------------------------------------------------------
# Test

File: `test.php`  
Program for testing `parse.php` and `interpret.py` files

### About

File `test.php` is a program for testing programs `parse.php` and `interpret.py`. The program for the first sets
arguments formats some of them and checks validity. After that, the program generates HTML heads and styles. The program gets files by function [getFiles](#getFiles), then creates an array of tests and cycles through files, and transforms the files into tests. After this operation, the program has a list of Tests with attached files for source, input, output, and return code. Then the program makes another cycle for tests, generates missing input and returns code files,
runs tests for parse, and interprets according to parse-only and int-only arguments. After tests, the program checks
if the expected output files and generated output files are the same. In this phase, the program has all the information about
tests. Then it generates an HTML representation for every test. The HTML page is done and printed to stdout. The program
clears the temporary files if no clean argument not passed.

## Functions

Functions used in program:
- **printErrorMessage** - Prints error message and exit with return code which is passed as argument
- **printHelpMessage** - Prints help message for user
- **preStringInArray** - Checks if some element in the array starts with preString
- **[getFiles](#getfiles)** - Get files from directory
- **generateSideBar** - Generate HTML sidebar

### getFiles

The function gets the directory name and checks if it exists. Then gets all the files from directory which ends with .src,
.in, .out or .rc extension. If --recursive argument passes, the function searches all the subdirectories in the
directory.

## Classes

Classes used in `test.php` program:
- **[Test](#Test)** - Class contains

### Class Test

#### Variables

The class contains the path and name for the test, files with source, input, output, and return code. Missing input and return
the code file is generated with the function generateMissingFiles. Further, this class contains a file with the output generated by
parse and interpret tests, return code generated by these tests, and a boolean if output files are identical if there
is enough data for comparison.

#### Functions

The Constructor sets the name and path from the passed string, setFile function sets the file by its extension, getId function returns
pathname concatenate with file name, getResult returns the result of the test according to the return code and expected
return cod, and by outputs identity, generateMissingFiles function generates input and return code (with content 0)
files, parseTest runs test for parser with source file as input and save the file into the output file, interpretTest runs
test for interpreting with source file from src or output file according to intOnly argument, setOutputsIdentity checks
differences between output and expected output if it has enough data for comparison, generateFile creates a new file with
passed extension and content, and printTest function prints the test data into HTML representation. There are a few more
functions for generating HTML elements.

## Program run

A program run as a list:
1. Set arguments of the program
2. Generate HTML head and styles for tags
3. Get the files for the tests
4. Transform files into tests
5. Generate missing files for the tests
6. Run parse and interpret tests
7. Set outputs identity
8. Generate HTML sidebar and table with summarize
9. Print tests as HTML representation
10. Clean temporary files according to no clean argument

-----------------------------------------------------------------------------------------------------------------------
## Author

Adam Dzurilla  
xdzuri00