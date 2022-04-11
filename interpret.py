"""
-----------------------------------------------------------------------------
@project 	:		Interpreter IPP 2022
@file 		:		interpret.py
@email		:		xdzuri00@stud.fit.vutbr.cz
@author 	:		Adam Dzurilla, xdzuri00
-----------------------------------------------------------------------------
"""

import sys
import xml.etree.ElementTree as ET
from enum import Enum

# region ERROR_CODES
NO_ERROR = 0
ERROR_INVALID_PARAMS_COMBINATION = 10
ERROR_OPEN_INPUT_FILE = 11
ERROR_OPEN_OUTPUT_FILE = 12
ERROR_XML_NOT_WELL_FORMED = 31
ERROR_XML_UNEXPECTED_STRUCTURE = 32
ERROR_SEMANTIC_CONTROL = 52  # Using of undefined label, variable redefinition
ERROR_WRONG_OPERANDS = 53  # Wrong operands types
ERROR_NON_EXISTENT_VARIABLE = 54  # frame exists but variable don't
ERROR_NON_EXISTENT_FRAME = 55  # e.g. reading from empty frame
ERROR_MISSING_VALUE = 56  # in variable, in frame etc.
ERROR_WRONG_OPERAND_VALUE = 57  # e.g. dividing by zero, wrong exit return
ERROR_WORKING_WITH_STRING = 58
ERROR_INTERNAL = 99


# endregion


def print_error_message(message, error_code):
    """
	The function prints error message on the stderr (Standard error output)
	@param message:		Gets message which will be printed on the stderr
	@param error_code:	The function exits with the error code
	"""
    sys.stderr.write('ERROR: ' + message + '\n')
    exit(error_code)


def print_help_message():
    """
	The function prints help message
	"""
    print("Usage:")
    print("\tpython3.8 interpret.py [OPTIONS] <OPTIONAL_STDIN")
    print()
    print("Options:")
    print("\t--help\t\t\tDisplay this message")
    print("\t--source=FILE\t\tSet source file")
    print("\t--input=FILE\t\tSet input file")
    print()
    print("Exit status:")
    print("\t0\t\tOK,")

    print("\t10\t\tInvalid combination of the parameters,")
    print("\t11\t\tError in opening input file,")
    print("\t12\t\tError in opening output file,")

    print("\t31\t\tXml file is not well-formed,")
    print("\t32\t\tUnexpected structure of the xml file,")

    print("\t52\t\tSemantic error,")
    print("\t53\t\tWrong type of the operand,")
    print("\t54\t\tWorking with non existent variable,")
    print("\t55\t\tWorking with non existent frame,")
    print("\t56\t\tMissing value,")
    print("\t57\t\tWrong value of the operand,")
    print("\t58\t\tString error,")

    print("\t99\t\tError internal (e.g. memory allocation, program proceeds values wrongly and later occurred error)")
    print()
    print("This is help message for the program \"interpret.py\"")
    print("For the full documentation see: readme2.md")

    exit(NO_ERROR)


class Type(Enum):
    """
    Types for variables
    """
    UNINITIALIZED = 0
    STRING = 1
    INT = 2
    BOOLEAN = 3
    NULL = 4


class Label:
    """
    The label contains name and order attributes
    """

    def __init__(self, name, order):
        self.name = name
        self.order = order


class Instruction:
    """
    The instruction contains order, opcode and arguments attributes
	"""

    def __init__(self, order: int, opcode: str, arguments):
        """
        @param order: Order number
        @param opcode: Opcode of instruction
        @param arguments: List of arguments
        """
        self.order = order
        self.opcode = opcode
        self.arguments = arguments
        if self.order < 1:
            # The order controls negative number
            print_error_message('Invalid instruction order number', ERROR_XML_UNEXPECTED_STRUCTURE)

    def get_order(self):
        """
        @return: the order number
        """
        return self.order


class Argument:
    """
	The argument contains type and value attributes
	"""

    def __init__(self, arg_type: str, value):
        """
        @param arg_type: Type of the argument
        @param value: Argument's value
        """
        self.type: str = arg_type
        self.value = '' if value is None else value  # If value is None then assigns empty string


class Variable:
    """
	The variable contains name, type, value and is_init attributes
	"""

    def __init__(self, variable_name, variable_type=None, variable_value=None):
        """
        @param variable_name: Name of the variable
        @param variable_type: Type of the variable
        @param variable_value: Value of the variable
        """
        self.name = variable_name
        self.type = Type.UNINITIALIZED
        self.value = variable_value

        # Sets type and value of the variable by functions
        if variable_type is not None:
            self.set_type(variable_type)
            self.set_value(variable_value)

        # Defines is_init by type initialization
        self.is_init = False if self.type is Type.UNINITIALIZED else True

    def set_name(self, name):
        """
        Sets name of the variable
        @param name: New name of the variable
        """
        self.name = name

    def set_type(self, var_type):
        """
        Sets type by string
        @param var_type: Translate var_type assigned by string into Type
        """
        if type(var_type) == str:
            if var_type == 'string':
                self.type = Type.STRING
            elif var_type == 'int':
                self.type = Type.INT
            elif var_type == 'bool':
                self.type = Type.BOOLEAN
            elif var_type == 'nil':
                self.type = Type.NULL
            else:
                print_error_message('Unknown type value: ' + var_type, ERROR_XML_UNEXPECTED_STRUCTURE)
        elif type(var_type) == Type:
            self.type = var_type
        else:
            print_error_message('Program incorrectly proceeds variable type', ERROR_INTERNAL)

    def set_value(self, value):
        """
        Sets value to the variable
        @param value:
        """
        if self.type is Type.STRING:
            self.value = str(value)
        elif self.type is Type.INT:
            try:
                self.value = int(value)
            except ValueError:
                print_error_message('Trying assign non int value to integer', ERROR_XML_UNEXPECTED_STRUCTURE)
        elif self.type is Type.BOOLEAN:
            self.value = value == 'true'
        elif self.type is Type.NULL:
            self.value = None
        else:
            print_error_message('Program incorrectly processed variable\'s type\nClass Variable\nFunction set_value',
                                ERROR_INTERNAL)

    def get_value(self):
        """
        @return: value of the variable
        """
        return self.value

    def init_control(self):
        """
        Raises error if variable is not initialized
        """
        if self.is_init is False:
            print_error_message('Missing value in variable: ' + self.name, ERROR_MISSING_VALUE)


class Frame:
    """
	The frame contains list of variables as its attribute
	"""

    def __init__(self):
        self.variables = []

    def add(self, variable: Variable):
        """
        The function checks variable redefinition
        then add it to the list
        @param variable: The variable which will be added to the list of variables
        """
        for var in self.variables:
            if var.name == variable.name:
                print_error_message('Variable redefinition: ' + variable.name, ERROR_SEMANTIC_CONTROL)

        self.variables.append(variable)

    def remove(self, variable: Variable):
        """
        The function removes variable from list of variables
        @param variable: The variable which will be deleted
        """
        self.variables.remove(variable)

    def contain_var(self, var_name: str):
        """
        The function checks if variable is in list of variables
        @param var_name: Name for check
        @return: If variable is in frame
        """
        for var in self.variables:
            if var.name == var_name:
                return True

        return False

    def get_variable(self, var_name: str):
        """
        Gets variable from frame by its name
        @param var_name: Name of the variable which will be returned
        """
        for var in self.variables:
            if var.name == var_name:
                return var

        # Raise error if variable is not in the list -> Working with undefined variable
        print_error_message('Non existent variable: ' + var_name, ERROR_NON_EXISTENT_VARIABLE)

    def update_var(self, variable: Variable):
        """
        Remove old variable and then add new one with the same name
        @param variable: New variable
        """
        self.remove(self.get_variable(variable.name))
        self.add(variable)

    def print_content_to_stderr(self):
        for var in self.variables:
            sys.stderr.write(
                '\t' + var.name + ' '
                + str(var.type) + ' '
                + str(var.value) + ' '
                + str(var.is_init) + '\n'
            )


class Frames:
    """
    The frame contains global_frame, local_frames, local_frame and temporary_frame attributes
    """

    def __init__(self):
        self.global_frame = Frame()
        self.local_frames = []
        self.temporary_frame = None

    def get_gf(self) -> Frame:
        """
        @return: Global frame
        """
        return self.global_frame

    def get_lf(self) -> Frame:
        """
        Returns last element of the list of the local frames
        @return: Local frame
        """
        if not self.local_frames:
            print_error_message('Undefined local frame\nClass Frames\nInstruction get_lf', ERROR_NON_EXISTENT_FRAME)

        return self.local_frames[-1]

    def get_tf(self) -> Frame:
        """
        Checks if temporary frame is initialized
        then returns it
        @return: Temporary frame
        """
        if self.temporary_frame is None:
            print_error_message(
                'Undefined temporary frame\nClass Frames\nInstruction get_tf',
                ERROR_NON_EXISTENT_FRAME
            )

        return self.temporary_frame

    def create_tf(self):
        """
        Creates new temporary frame
        """
        self.temporary_frame = Frame()

    def push_frame(self):
        """
        Pushs temporary frame in list of local frames and make it uninitialized
        """
        self.local_frames.append(self.get_tf())
        self.temporary_frame = None

    def pop_frame(self):
        """
        Checks local frames emptiness
        then pop last element from list of local frames
        """
        if not self.local_frames:
            print_error_message('Undefined local frame\nInstruction: POPFRAME', ERROR_NON_EXISTENT_FRAME)

        self.temporary_frame = self.local_frames.pop()

    def print_frames_to_stderr(self):
        sys.stderr.write('The format of the variables: NAME TYPE VALUE IS_INITIALIZED\n')
        sys.stderr.write('The content of the global frame:\n')
        self.get_gf().print_content_to_stderr()

        if self.local_frames:
            sys.stderr.write('The content of the local frame:\n')
            self.get_lf().print_content_to_stderr()
        else:
            sys.stderr.write('The local frame is uninitialized\n')

        if self.temporary_frame is not None:
            sys.stderr.write('The content of the temporary frame\n')
            self.get_tf().print_content_to_stderr()
        else:
            sys.stderr.write('The temporary frame is uninitialized:\n')


class Stack:
    """
    The stack contains list of undefined type as its attribute
    """

    def __init__(self):
        self.list = []

    def push(self, value):
        """
        Appends value to the list
        @param value: The value which will be appended
        """
        self.list.append(value)

    def pop(self):
        """
        Checks if the list is not empty
        then pop last element
        @return: The last element of the list
        """
        if self.list:
            return self.list.pop()
        else:
            # Emptiness raises error
            print_error_message('Pop from empty stack', ERROR_MISSING_VALUE)

    def clear(self):
        while self.list:
            self.pop()


def math_operation(name, operand1: Variable, operand2: Variable, operation: str) -> Variable:
    """
    Calculates math problem
    @param name: Name of the result variable
    @param operand1: First operand
    @param operand2: Second operand
    @param operation: Mathematical operation
    @return: Int variable with result
    """
    operand1.init_control()
    operand2.init_control()
    # Operation can be called only by INTs types
    if operand1.type is not Type.INT or operand2.type is not Type.INT:
        print_error_message('Wrong type\nFunction: math_operation', ERROR_WRONG_OPERANDS)

    # Process mathematical operation
    result = 0
    if operation == '+':
        # Addition
        result = operand1.get_value() + operand2.get_value()
    elif operation == '-':
        # Substitution
        result = operand1.get_value() - operand2.get_value()
    elif operation == '*':
        # Multiplication
        result = operand1.get_value() * operand2.get_value()
    elif operation == '//':
        # Division
        try:
            result = operand1.get_value() // operand2.get_value()
        except ZeroDivisionError:
            print_error_message('Division by zero', ERROR_WRONG_OPERAND_VALUE)

    else:
        # Unknown operator raises error
        print_error_message('Wrong operation\nFunction: math_operation', ERROR_INTERNAL)

    return Variable(name, Type.INT, result)


def vars_compare(var1, var2, operation) -> bool:
    """
    The function compares two variables
    @param var1:        First variable
    @param var2:        Second variable
    @param operation:   Operation e.g. EQ, NEQ, LT, GT
    @return:            The veracity of the operation
    """
    # Checks initializations
    var1.init_control()
    var2.init_control()

    # Checks type compatibility
    if var1.type != var2.type:
        print_error_message(
            'Different types in comparison\nFunction: arguments_comparison',
            ERROR_WRONG_OPERANDS
        )

    # Proceed operation between arguments
    if operation == '==':
        # Equalisation
        return True if var1.value == var2.value else False
    elif operation == '!=':
        # Not equalisation
        return True if var1.value != var2.value else False
    elif operation == '>':
        # Less than
        return True if var1.value > var2.value else False
    elif operation == '<':
        # Greater than
        return True if var1.value < var2.value else False
    else:
        # Unknown operator raises error
        print_error_message('Unknown operator\nFunction: arguments_comparison', ERROR_INTERNAL)


def lt_gt_eq(name, var1: Variable, var2: Variable, op: str) -> Variable:
    """
    Logical expression LT, GT, EQ
    @param name:    Name of the result variable
    @param var1:    First variable
    @param var2:    Second variable
    @param op:      Logical operation
    @return:        Boolean variable with result
    """
    # Initialization control
    var1.init_control()
    var2.init_control()

    # Gets a result
    result_value = True if vars_compare(var1, var2, op) else False

    # Creates a result variable
    result_var = Variable(name, Type.BOOLEAN, result_value)

    return result_var


def and_or_not(name, var1: Variable, var2, op) -> Variable:
    """
    Logical operations AND, OR, NOT
    @param name:    Name of the result variable
    @param var1:    First variable
    @param var2:    Second variable or None in NOT function
    @param op:      Logical operation
    @return:        Boolean variable with result
    """
    var1.init_control()

    # Checks the validity of the variable's type
    if var1.type is not Type.BOOLEAN:
        print_error_message('Wrong operands types\nInstruction: ' + op.upper(), ERROR_WRONG_OPERANDS)

    # Performs logical operation
    if op == 'and' or op == 'or':
        var2.init_control()

        # Checks the type of the new variable
        if var2.type is not Type.BOOLEAN:
            print_error_message('Wrong operands types\nInstruction: ' + op.upper(), ERROR_WRONG_OPERANDS)

        if op == 'and':
            # AND
            result_value = var1.value and var2.value
        else:
            # OR
            result_value = var1.value or var2.value
    else:
        # NOT
        result_value = not var1.value

    return Variable(name, Type.BOOLEAN, result_value)


def int2char(name, var1: Variable) -> Variable:
    """
    Translates integer to char
    @param name:    Name of the result variable
    @param var1:    Integer variable
    @return:        String variable with result
    """
    var1.init_control()

    # Variable has to be integer
    if var1.type is not Type.INT:
        print_error_message('Wrong operands types\nFunction: INT2CHAR', ERROR_WRONG_OPERANDS)

    # Transforms int to the char and catches errors TypeError and ValueError
    char = None
    try:
        char = chr(var1.value)
    except TypeError:
        print_error_message('Wrong type input\nInstruction: INT2CHAR', ERROR_WORKING_WITH_STRING)
    except ValueError:
        print_error_message('Value error\nInstruction: INT2CHAR', ERROR_WORKING_WITH_STRING)

    # Creates a return variable
    result_var = Variable(name, Type.STRING, char)

    return result_var


def stri2int(name, var_string: Variable, var_int: Variable) -> Variable:
    """
    Gets ordinal value of char at the string position
    @param name:        Name of the result variable
    @param var_string:  String variable
    @param var_int:     Position
    @return:            Int variable with result
    """
    # Initialization controls
    var_string.init_control()
    var_int.init_control()

    # Checks the types validity
    if var_string.type is not Type.STRING or var_int.type is not Type.INT:
        print_error_message('Incompatible types\nFunction: STRI2INT', ERROR_WRONG_OPERANDS)

    # Checks the index validity
    if len(var_string.value) <= var_int.value:
        print_error_message('Index outside string\nFunction: STRI2INT', ERROR_WORKING_WITH_STRING)

    # Gets ordinal value of a char at the position
    result_value = ord(var_string.value[var_int.value])

    # Creates a result variable
    result_var = Variable(name, Type.INT, result_value)

    return result_var


class Program:
    """
    The program contains iteration, instructions, labels, frames, input_lines, stack and stack_calls as its attributes
    The program contains functions for working with its attributes, and functions for instructions
    """

    def __init__(self, input_lines: list):
        """
        @param input_lines: List of inputs
        """
        self.iteration = 0
        self.number_of_proceeded_functions = 0
        self.instructions = []
        self.labels = []
        self.frames = Frames()
        self.input_lines = input_lines
        self.stack = Stack()  # Stack of variables
        self.stack_calls = Stack()  # Stack of calls

    def add_label(self, label):
        """
        Checks label validity, then add it to the list of labels
        @param label:   Label which will be added to the list of labels
        """
        for lab in self.labels:
            if lab.name == label.name:
                print_error_message('Label redefinition: ' + label.name, ERROR_SEMANTIC_CONTROL)

        # Appending the label to the list of labels
        self.labels.append(label)

    def get_label(self, label_name: str):
        """
        Gets a label from the list by name
        If the label with the name does not exist then raises undefined label error
        """

        labels = self.labels

        # Cycle through labels
        for label in labels:
            if label.name == label_name:
                return label

        # Label was not found in list of labels
        print_error_message('Undefined label', ERROR_SEMANTIC_CONTROL)

    def load_labels(self):
        """
        Loops through instructions and add labels to the list of labels
        """
        for ins in self.instructions:
            if ins.opcode == 'LABEL':
                self.add_label(Label(ins.arguments[0].value, ins.order))

    def add_instruction(self, instruction):
        """
        Checks instruction validity, then add it to the list of instructions
        @param instruction:     Instruction for check and append
        """

        # List of the valid instructions
        valid_instructions = ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN',
                              'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT',
                              'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT', 'STRLEN', 'GETCHAR', 'SETCHAR',
                              'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK']

        valid_instructions_extension = ['CLEARS', 'ADDS', 'SUBS', 'MULS', 'IDIVS', 'LTS', 'GTS', 'EQS', 'ANDS',
                                        'ORS', 'NOTS', 'INT2CHARS', 'STRI2INTS', 'JUMPIFEQS', 'JUMPIFNEQS']

        # Check OPCODE validity
        if instruction.opcode not in valid_instructions and instruction.opcode not in valid_instructions_extension:
            print_error_message('Invalid instruction opcode: ' + instruction.opcode, ERROR_XML_UNEXPECTED_STRUCTURE)

        # Check ORDER duplication validity
        for ins in self.instructions:
            if ins.order == instruction.order:
                print_error_message('Duplicate instruction order', ERROR_XML_UNEXPECTED_STRUCTURE)

        # Append the instruction to the list of instructions
        self.instructions.append(instruction)

    def get_instruction(self) -> Instruction:
        """
        @return: Instruction by iteration number
        """
        return self.instructions[self.iteration]

    def sort_instructions(self):
        """
        Sorts instructions by order
        then rewrites orders from one incrementing by one
        """
        # Sorts by ORDER
        self.instructions.sort(key=Instruction.get_order)

        # Rewrites ORDER
        rewrite_order = 1
        for ins in self.instructions:
            ins.order = rewrite_order
            rewrite_order += 1

    def get_argument(self, position) -> Argument:
        """
        The function gets the argument from currently proceeded instruction at the position
        @param position: The position of argument in instruction list
        @return: The argument at the position
        """
        # Gets currently proceeded instruction
        instruct = self.get_instruction()

        # Compares the position and the list length due to the validity
        if len(instruct.arguments) <= position:
            print_error_message('Trying to get the argument outside the list', ERROR_XML_UNEXPECTED_STRUCTURE)

        # Returns the argument at the position
        return instruct.arguments[position]

    def get_frame(self, frame_opcode: str = None) -> Frame:
        """
        Returns frame by frame_opcode
        @param frame_opcode: Label of the frame
        @return: Frame
        """
        # If frame_opcode is empty, it loads it from the first instruction argument
        if frame_opcode is None:
            arg = self.get_argument(0)
            frame_opcode = arg.value[0:2]

        # Returns frame by frames_opcode
        if frame_opcode == 'GF':
            # Global frame
            return self.frames.get_gf()
        elif frame_opcode == 'LF':
            # Local frame
            return self.frames.get_lf()
        elif frame_opcode == 'TF':
            # Temporary frame
            return self.frames.get_tf()
        else:
            # Unknown frame label raises error
            print_error_message('Unknown frame opcode: ' + frame_opcode, ERROR_XML_UNEXPECTED_STRUCTURE)

    def get_var(self, argument: Argument) -> Variable:
        """
        Translates argument into variable
        @param argument: Argument which will be translated
        @return: Translated variable
        """
        # Gets variable
        if argument.type == 'var':
            # Gets the variable from the frame
            frame = argument.value[0:2]
            name = argument.value[3:]
            var = self.get_frame(frame).get_variable(name)
        else:
            # Gets the variable from the argument
            var = Variable(None, argument.type, argument.value)

        return var

    def is_iteration_at_the_end(self) -> bool:
        """
        Checks if last instruction was proceeded
        @return: The veracity of the function
        """
        return self.iteration == len(self.instructions)

    def call_function(self, function_opcode: str):
        """
        The function calls another function by the function_opcode, then increases iteration
        @param function_opcode: OPCODE of proceeded function
        """
        if function_opcode == "MOVE":
            self.ins_move()
        elif function_opcode == "CREATEFRAME":
            self.ins_createframe()
        elif function_opcode == "PUSHFRAME":
            self.ins_pushframe()
        elif function_opcode == "POPFRAME":
            self.ins_popframe()
        elif function_opcode == "DEFVAR":
            self.ins_defvar()
        elif function_opcode == "CALL":
            self.ins_call()
        elif function_opcode == "RETURN":
            self.ins_return()
        elif function_opcode == "PUSHS":
            self.ins_pushs()
        elif function_opcode == "POPS":
            self.ins_pops()
        elif function_opcode == "ADD":
            self.ins_add()
        elif function_opcode == "SUB":
            self.ins_sub()
        elif function_opcode == "MUL":
            self.ins_mul()
        elif function_opcode == "IDIV":
            self.ins_idiv()
        elif function_opcode == "LT":
            self.ins_lt()
        elif function_opcode == "GT":
            self.ins_gt()
        elif function_opcode == "EQ":
            self.ins_eq()
        elif function_opcode == "AND":
            self.ins_and()
        elif function_opcode == "OR":
            self.ins_or()
        elif function_opcode == "NOT":
            self.ins_not()
        elif function_opcode == "INT2CHAR":
            self.ins_int2char()
        elif function_opcode == "STRI2INT":
            self.ins_stri2int()
        elif function_opcode == "READ":
            self.ins_read()
        elif function_opcode == "WRITE":
            self.ins_write()
        elif function_opcode == "CONCAT":
            self.ins_concat()
        elif function_opcode == "STRLEN":
            self.ins_strlen()
        elif function_opcode == "GETCHAR":
            self.ins_getchar()
        elif function_opcode == "SETCHAR":
            self.ins_setchar()
        elif function_opcode == "TYPE":
            self.ins_type()
        elif function_opcode == "LABEL":
            self.ins_label()
        elif function_opcode == "JUMP":
            self.ins_jump()
        elif function_opcode == "JUMPIFEQ":
            self.ins_jumpifeq()
        elif function_opcode == "JUMPIFNEQ":
            self.ins_jumpifneq()
        elif function_opcode == "EXIT":
            self.ins_exit()
        elif function_opcode == "DPRINT":
            self.ins_dprint()
        elif function_opcode == "BREAK":
            self.ins_break()
        else:
            # Unknown instruction raises error
            print_error_message('Unknown instruction ' + function_opcode, ERROR_XML_UNEXPECTED_STRUCTURE)
        self.iteration += 1
        self.number_of_proceeded_functions += 1

    # region Instructions
    def ins_move(self):
        """
        The function moves a value from the second argument into the first one
        """
        # Loads dest_var
        dest_var = self.get_var(self.get_argument(0))

        # Checks the existence of the variable
        if not self.get_frame().contain_var(dest_var.name):
            print_error_message('Attempt in working with non existent variable', ERROR_NON_EXISTENT_VARIABLE)

        # Gets the variable from the second argument
        var = self.get_var(self.get_argument(1))
        # Control of the initialization
        var.init_control()

        # Rewrites the name and then updates the variable in the frame
        var.set_name(dest_var.name)
        self.get_frame().update_var(var)

    def ins_createframe(self):
        """
        Creates temporary frame
        """
        self.frames.create_tf()

    def ins_pushframe(self):
        """
        Moves temporary frame to the list of the local frames
        and then adds it to the list of the local frames
        """
        self.frames.push_frame()

    def ins_popframe(self):
        """
        Moves the local frame to the temporary frame
        and then pops it from the list of local frames
        """
        self.frames.pop_frame()

    def ins_defvar(self):
        """
        Defines a new variable on frame determined by its argument
        """
        # Loads the argument
        arg = self.get_argument(0)

        # Gets a name from the variable
        name = arg.value[3:]

        # Creates a new uninitialized variable
        self.get_frame().add(Variable(name))

    def ins_call(self):
        """
        Calls the label and pushs incremented iteration on the stack of calls
        """
        # Label argument
        arg1 = self.get_argument(0)

        # Label where program jumps
        label = self.get_label(arg1.value)

        # Pushs incremented iteration on the stack of calls
        self.stack_calls.push(self.iteration + 1)

        # Jumps on label
        self.iteration = label.order - 1

    def ins_return(self):
        """
        Jumps back on the iteration
        """
        self.iteration = self.stack_calls.pop()

    def ins_pushs(self):
        """
        Pushs the variable on the stack
        """
        arg = self.get_argument(0)

        if arg.type == 'label':
            label = self.get_label(arg.value)
            self.stack.push(label)
        else:
            var = self.get_var(arg)
            self.stack.push(var)

    def ins_pops(self):
        """
        Pops the variable from the stack
        """
        # Loads first argument as a variable
        var = self.get_var(self.get_argument(0))

        # Gets the variable from the stack
        var_from_stack = self.stack.pop()

        # Rewrites its name
        var_from_stack.set_name(var.name)

        # Updates the variable on the frame
        self.get_frame().update_var(var_from_stack)

    def ins_add(self):
        """
        Addition
        """
        destination = self.get_var(self.get_argument(0))
        operand1 = self.get_var(self.get_argument(1))
        operand2 = self.get_var(self.get_argument(2))

        result_var = math_operation(destination.name, operand1, operand2, '+')

        self.get_frame().update_var(result_var)

    def ins_sub(self):
        """
        Substitution
        """
        destination = self.get_var(self.get_argument(0))
        operand1 = self.get_var(self.get_argument(1))
        operand2 = self.get_var(self.get_argument(2))

        result_var = math_operation(destination.name, operand1, operand2, '-')

        self.get_frame().update_var(result_var)

    def ins_mul(self):
        """
        Multiplication
        """
        destination = self.get_var(self.get_argument(0))
        operand1 = self.get_var(self.get_argument(1))
        operand2 = self.get_var(self.get_argument(2))

        result_var = math_operation(destination.name, operand1, operand2, '*')

        self.get_frame().update_var(result_var)

    def ins_idiv(self):
        """
        INT division
        """
        destination = self.get_var(self.get_argument(0))
        operand1 = self.get_var(self.get_argument(1))
        operand2 = self.get_var(self.get_argument(2))

        result_var = math_operation(destination.name, operand1, operand2, '//')

        self.get_frame().update_var(result_var)

    def ins_lt(self):
        """
        Less than
        """
        var_dest = self.get_var(self.get_argument(0))

        var1 = self.get_var(self.get_argument(1))
        var2 = self.get_var(self.get_argument(2))

        result_var = lt_gt_eq(var_dest.name, var1, var2, '<')

        self.get_frame().update_var(result_var)

    def ins_gt(self):
        """
        Greater than
        """
        var_dest = self.get_var(self.get_argument(0))

        var1 = self.get_var(self.get_argument(1))
        var2 = self.get_var(self.get_argument(2))

        result_var = lt_gt_eq(var_dest.name, var1, var2, '>')

        self.get_frame().update_var(result_var)

    def ins_eq(self):
        """
        Equal
        """
        var_dest = self.get_var(self.get_argument(0))

        var1 = self.get_var(self.get_argument(1))
        var2 = self.get_var(self.get_argument(2))

        result_var = lt_gt_eq(var_dest.name, var1, var2, '==')

        self.get_frame().update_var(result_var)

    def ins_and(self):
        """
        AND logical operation
        """
        var_dest = self.get_var(self.get_argument(0))

        var1 = self.get_var(self.get_argument(1))
        var2 = self.get_var(self.get_argument(2))

        result_var = and_or_not(var_dest.name, var1, var2, 'and')

        self.get_frame().update_var(result_var)

    def ins_or(self):
        """
        OR logical operation
        """
        var_dest = self.get_var(self.get_argument(0))

        var1 = self.get_var(self.get_argument(1))
        var2 = self.get_var(self.get_argument(2))

        result_var = and_or_not(var_dest.name, var1, var2, 'or')

        self.get_frame().update_var(result_var)

    def ins_not(self):
        """
        NOT logical operation
        """
        var_dest = self.get_var(self.get_argument(0))

        var1 = self.get_var(self.get_argument(1))

        result_var = and_or_not(var_dest.name, var1, None, 'not')

        self.get_frame().update_var(result_var)

    def ins_int2char(self):
        """
        Translates int to the char value
        """
        var_dest = self.get_var(self.get_argument(0))
        var_int = self.get_var(self.get_argument(1))

        result_var = int2char(var_dest.name, var_int)

        self.get_frame().update_var(result_var)

    def ins_stri2int(self):
        """
        Saves ordinal value of char in string at the position to the target variable
        """
        # Gets a destination variable
        var_dest = self.get_var(self.get_argument(0))

        # Gets a string and int parameters
        var_string = self.get_var(self.get_argument(1))
        var_int = self.get_var(self.get_argument(2))

        # Gets a variable for update
        result_variable = stri2int(var_dest.name, var_string, var_int)

        self.get_frame().update_var(result_variable)

    def ins_read(self):
        """
        Reads from input file and then saves the value to the variable
        """
        # Destination variable
        var1 = self.get_var(self.get_argument(0))

        # Gets input value and removes it from the input_lines list
        input_value = self.input_lines[0]
        del self.input_lines[0]

        # New variable
        new_variable = Variable(
            var1.name,
            self.get_argument(1).value,
            input_value
        )

        self.get_frame().update_var(new_variable)

    def ins_write(self):
        """
        The function prints the argument to the stdout
        """
        # Gets variable from the first argument and then checks its initialization
        var = self.get_var(self.get_argument(0))
        var.init_control()

        # Prints variable
        if var.type is Type.NULL:
            print('', end='')
        elif var.type is Type.STRING:
            print(translate_to_normal_string(var.value), end='')
        elif var.type is Type.BOOLEAN:
            if var.value is True:
                print('true', end='')
            else:
                print('false', end='')
        else:
            print(var.value, end='')

    def ins_concat(self):
        """
        The function concatenates two strings
        """
        dest_var = self.get_var(self.get_argument(0))

        # Checks initialization of the variables
        var1 = self.get_var(self.get_argument(1))
        var1.init_control()
        var2 = self.get_var(self.get_argument(2))
        var2.init_control()

        # Checks the types of the variables
        if var1.type is not Type.STRING or var2.type is not Type.STRING:
            print_error_message('Wrong type of the operand\nInstruction: CONCAT', ERROR_WRONG_OPERANDS)

        new_variable = Variable(
            dest_var.name,
            'string',
            var1.get_value() + var2.get_value()
        )

        self.get_frame().update_var(new_variable)

    def ins_strlen(self):
        """
        Saves length of the string to the target variable
        """
        # Loads arguments and checks initialization
        var1 = self.get_var(self.get_argument(0))
        var2 = self.get_var(self.get_argument(1))
        var2.init_control()

        # Checks type validity
        if var2.type is not Type.STRING:
            print_error_message('Wrong operand type\nInstruction: STRLEN', ERROR_WRONG_OPERANDS)

        # Gets a result value
        result_value = len(var2.value)

        # Creates a result variable
        result_variable = Variable(var1.name, Type.INT, result_value)

        self.get_frame().update_var(result_variable)

    def ins_getchar(self):
        """
        Saves one char to the first argument from string (second argument) at the position (third argument)
        """
        # Loads arguments and check their validity
        var_dest = self.get_var(self.get_argument(0))
        var_string = self.get_var(self.get_argument(1))
        var_string.init_control()
        var_int = self.get_var(self.get_argument(2))
        var_int.init_control()

        # Checks the types of the variables
        if var_string.type is not Type.STRING or var_int.type is not Type.INT:
            print_error_message('Wrong operand type\nInstruction: GETCHAR', ERROR_WRONG_OPERANDS)

        # Checks index validity
        if len(var_string.value) <= var_int.value:
            print_error_message('Index outside string\nInstruction: GETCHAR', ERROR_WORKING_WITH_STRING)

        # Gets a result value
        result_value = var_string.value[var_int.value]

        # Creates a result variable
        result_variable = Variable(var_dest.name, Type.STRING, result_value)

        self.get_frame().update_var(result_variable)

    def ins_setchar(self):
        """
        Modify string (first argument) at the position (second argument) as new char (third argument)
        """
        # Loads arguments and checks the initializations
        var_dest = self.get_var(self.get_argument(0))
        var_dest.init_control()
        var_int = self.get_var(self.get_argument(1))
        var_int.init_control()
        var_char = self.get_var(self.get_argument(2))
        var_char.init_control()

        # Checks the types of the variables
        if var_dest.type is not Type.STRING or var_int.type is not Type.INT or var_char.type is not Type.STRING:
            print_error_message('Wrong operand type\nInstruction: SETCHAR', ERROR_WRONG_OPERANDS)

        # Rewrite dest string
        var_dest.value[var_int.value] = var_char.value[0]

        self.get_frame().update_var(var_dest)

    def ins_type(self):
        """
        Saves type of the variable (second argument) to the destination variable (first argument)
        """
        var_dest = self.get_var(self.get_argument(0))
        var = self.get_var(self.get_argument(1))

        # Gets a result value by variable type
        result_value = ''
        if var.type is Type.STRING:
            result_value = 'string'
        elif var.type is Type.INT:
            result_value = 'int'
        elif var.type is Type.BOOLEAN:
            result_value = 'bool'
        elif var.type is Type.NULL:
            result_value = 'nil'

        result_variable = Variable(var_dest.name, Type.STRING, result_value)
        self.get_frame().update_var(result_variable)

    def ins_label(self):
        pass

    def ins_jump(self):
        """
        Jumps to the label
        """
        arg = self.get_argument(0)
        label = self.get_label(arg.value)
        self.iteration = label.order - 1

    def ins_jumpifeq(self):
        """
        Jumps to the label if the second and third arguments are equal
        """
        arg1 = self.get_argument(0)

        label: Label = self.get_label(arg1.value)

        var1 = self.get_var(self.get_argument(1))
        var2 = self.get_var(self.get_argument(2))

        if vars_compare(var1, var2, '=='):
            self.iteration = label.order - 1

    def ins_jumpifneq(self):
        """
        Jumps to the label if the second and third arguments are not equal
        """
        arg1 = self.get_argument(0)

        label: Label = self.get_label(arg1.value)

        var1 = self.get_var(self.get_argument(1))
        var2 = self.get_var(self.get_argument(2))

        if vars_compare(var1, var2, '!='):
            self.iteration = label.order - 1

    def ins_exit(self):
        """
        Exit program with return code (first argument)
        """
        var = self.get_var(self.get_argument(0))

        # Checks the type of the variable
        if var.type is not Type.INT:
            print_error_message('Wrong operand type\nInstruction: EXIT', ERROR_WRONG_OPERANDS)

        # Checks the value of the variable
        if not 0 <= var.value <= 49:
            print_error_message('Exit code outside allowed range\nInstruction: EXIT', ERROR_WRONG_OPERAND_VALUE)

        # Exits program with return code
        exit(var.value)

    def ins_dprint(self):
        """
        Prints message to the stderr
        """
        var = self.get_var(self.get_argument(0))
        sys.stderr.write(str(translate_to_normal_string(var.value)) + '\n')

    def ins_break(self):
        """
        Prints some information to the stderr
        """
        sys.stderr.write('The iteration number: ' + str(self.iteration) + '\n')
        sys.stderr.write('The number of the proceeded functions: ' + str(self.number_of_proceeded_functions) + '\n\n')
        self.frames.print_frames_to_stderr()

    # endregion

    # region Instructions extension

    def ins_clears(self):
        self.stack.clear()

    def ins_adds(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = math_operation(sym1.name, sym1, sym2, '+')

        self.stack.push(return_var)

    def ins_subs(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = math_operation(sym1.name, sym1, sym2, '-')

        self.stack.push(return_var)

    def ins_muls(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = math_operation(sym1.name, sym1, sym2, '*')

        self.stack.push(return_var)

    def ins_idivs(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = math_operation(sym1.name, sym1, sym2, '//')

        self.stack.push(return_var)

    def ins_lts(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = lt_gt_eq(sym1.name, sym1, sym2, '<')

        self.stack.push(return_var)

    def ins_gts(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = lt_gt_eq(sym1.name, sym1, sym2, '>')

        self.stack.push(return_var)

    def ins_eqs(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = lt_gt_eq(sym1.name, sym1, sym2, '==')

        self.stack.push(return_var)

    def ins_ands(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = and_or_not(sym1.name, sym1, sym2, 'and')

        self.stack.push(return_var)

    def ins_ors(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = and_or_not(sym1.name, sym1, sym2, 'or')

        self.stack.push(return_var)

    def ins_nots(self):
        sym1 = self.stack.pop()

        return_var = and_or_not(sym1.name, sym1, None, 'not')

        self.stack.push(return_var)

    def ins_int2chars(self):
        sym1 = self.stack.pop()

        return_var = int2char(sym1.name, sym1)

        self.stack.push(return_var)

    def ins_stri2ints(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()

        return_var = stri2int(sym1.name, sym1, sym2)

        self.stack.push(return_var)

    def ins_jumpifeqs(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()
        label = self.stack.pop()

        if vars_compare(sym1, sym2, '=='):
            self.iteration = label.order - 1

    def ins_jumpifneqs(self):
        sym2 = self.stack.pop()
        sym1 = self.stack.pop()
        label = self.stack.pop()

        if vars_compare(sym1, sym2, '!='):
            self.iteration = label.order - 1

    # endregion


def is_char_number(num: str) -> bool:
    """
    @param num: Number in string format
    @return: If char is number
    """
    return '0' <= num <= '9'


def translate_to_normal_string(source_string: str):
    """
    Translates IPPcode22 string to the normal string
    @param source_string: Source string which will be translated
    @return: Translated string
    """
    # Final string which will be translated
    final = ''

    # Variable for skipping chars
    skip = 0
    for index in range(len(source_string)):
        # Skipping chars
        if skip != 0:
            skip -= 1
            continue

        # Char at the index
        char = source_string[index]

        # Performs exceptions
        if char == '\\':
            # Backslash exception
            num1 = None
            num2 = None
            num3 = None

            # Load numbers
            try:
                num1 = source_string[index + 1]
                num2 = source_string[index + 2]
                num3 = source_string[index + 3]
            except IndexError:
                print_error_message('Backslash at the end of the string', ERROR_WORKING_WITH_STRING)

            # Checks if chars are numbers
            if not is_char_number(num1) or not is_char_number(num2) or not is_char_number(num3):
                print_error_message('Char after backslash has to be number', ERROR_WORKING_WITH_STRING)

            # Calculates the next three numbers after backslash
            num = 100 * int(num1) + 10 * int(num2) + int(num3)
            final += chr(num)
            skip = 3
        elif char == '&':
            # LT, GT, AMP exceptions
            if source_string[index + 1] == 'l':
                final += '<'
                skip = 3
            elif source_string[index + 1] == 'g':
                final += '>'
                skip = 3
            elif source_string[index + 1] == 'a':
                final += '&'
                skip = 4
            else:
                print_error_message('Unexpected code after ampersand', ERROR_WORKING_WITH_STRING)
        else:
            final += char

    return final


def check_arguments(arguments):
    """
	The program checks each argument and its forbidden combination, then prints error message
	and exits the program with the appropriate exit code
	@param arguments: List of arguments
	@return: Source file, Input lines
	"""
    # The initialization of source and input file
    source_file = None
    input_file = None

    # Cycle through arguments
    for arg in arguments:
        if arg == '--help':
            # Help argument
            if len(sys.argv) != 1:
                print_error_message('--help param can\'t be used with other parameters',
                                    ERROR_INVALID_PARAMS_COMBINATION)
            else:
                print_help_message()
        elif arg[0:9] == '--source=':
            # Source file argument
            source_file = arg[9:]
        elif arg[0:8] == '--input=':
            # Input file argument
            input_file = arg[8:]
        else:
            print_error_message('Unknown parameter: ' + arg, ERROR_INVALID_PARAMS_COMBINATION)

    if source_file is None:
        source_file = sys.stdin

    if input_file is None:
        input_lines = sys.stdin
    else:
        f = open(input_file, 'r')
        input_lines = f.read().splitlines()

    return source_file, input_lines


def load_xml(tree, program: Program):
    """
	The function gets xml file and iterates through it to get the instructions and their arguments
	@param tree: tree of xml file
	@param program:	The program class
	"""
    root = tree.getroot()

    # Checks root language
    if root.attrib['language'] != 'IPPcode22':
        print_error_message('Language of source file has to be \'IPPcode22\'', ERROR_XML_UNEXPECTED_STRUCTURE)

    # Cycle through the instructions
    for instruct in root:
        if instruct.tag != 'instruction':
            print_error_message('Unexpected element', ERROR_XML_UNEXPECTED_STRUCTURE)

        # Loads the arguments
        arguments = []
        for arg in instruct:
            arguments.append(Argument(arg.attrib['type'], arg.text))

        # Adds instructions to the program
        program.add_instruction(
            Instruction(
                int(instruct.attrib['order']),
                instruct.attrib['opcode'].upper(),
                arguments
            )
        )

    # Sorts instructions and rewrites their orders
    program.sort_instructions()

    # Loads the labels to the program list of labels
    program.load_labels()


def main():
    """
	Main program function
	"""
    arguments = sys.argv  # Load arguments into variable
    arguments.pop(0)  # Remove 'interpret.py' parameter from list

    # Checks arguments and sets the source_file and input_file
    source_file, input_lines = check_arguments(arguments)

    # Loads the xml tree and catches the exceptions
    tree = None
    try:
        tree = ET.parse(source_file)
    except FileNotFoundError:
        print_error_message('Source file was not found\nFile name: ' + source_file, ERROR_OPEN_INPUT_FILE)
    except PermissionError:
        print_error_message('Permission denied in opening file', ERROR_OPEN_INPUT_FILE)
    except (ET.ParseError, OSError):
        print_error_message('Fail in work with source_file', ERROR_OPEN_INPUT_FILE)

    # Creates new program
    my_program = Program(input_lines)

    # Loads the instructions into the program
    load_xml(tree, my_program)

    # The interpretation of the program
    while not my_program.is_iteration_at_the_end():
        my_program.call_function(my_program.get_instruction().opcode)


# The calling of the main function
if __name__ == "__main__":
    main()
