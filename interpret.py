# -----------------------------------------------------------------------------
# PROJECT 	:		Interpreter IPP 2022
# FILE 		:		interpret.py
# EMAIL		:		xdzuri00@stud.fit.vutbr.cz
# AUTHOR 	:		Adam Dzurilla, xdzuri00
# -----------------------------------------------------------------------------

# TODO: Documentation: STRI2INT, STRLEN, GETCHAR, SETCHAR, TYPE, EXIT, DPRINT, BREAK
# TODO: Help message

import sys
import xml.etree.ElementTree as ET
from enum import Enum

# region ERROR_CODES
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
    print("Usage: python3.8 interpret.py [OPTIONS] <STDIN")
    print("Options:")
    print("\t--help\t\tDisplay this message")
    print("\t--source=FILE\t\tSet source file")
    print("\t--input=FILE\t\tSet input file")
    print()
    print("Exit status:")
    print("\t0\t\tOK,")
    print("\t10\t\tInvalid parameters combination,")
    print("\t11\t\tError in opening input file")
    print("\t12\t\tError open output file")
    print("\t99\t\tError internal (e.g. memory allocation")
    print()
    print("This is help message for program \"interpret.py\"")
    print("For full documentation see: readme2.md")


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

    def set_type(self, var_type: str):
        """
        Sets type by string
        @param var_type: Translate var_type assigned by string into Type
        """
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
            print_error_message('Uninitialized variable: ' + self.name, ERROR_SEMANTIC_CONTROL)


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
        print_error_message('Undefined variable: ' + var_name, ERROR_NON_EXISTENT_VARIABLE)

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
            print_error_message('No local frame\nClass Frames\nInstruction get_lf', ERROR_NON_EXISTENT_FRAME)

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
            print_error_message('No local frame\nInstruction: POPFRAME', ERROR_NON_EXISTENT_FRAME)

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

        # Check OPCODE validity
        if instruction.opcode not in valid_instructions:
            print_error_message('Invalid instruction opcode: ' + instruction.opcode, ERROR_XML_UNEXPECTED_STRUCTURE)

        # Check ORDER duplication validity
        for ins in self.instructions:
            if ins.order == instruction.order:
                print_error_message('Duplicate instruction order', ERROR_XML_UNEXPECTED_STRUCTURE)

        # Append the instruction to the list of instructions
        self.instructions.append(instruction)

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

    def get_instructions(self):
        """
        @return: List of instructions
        """
        return self.instructions

    def get_instruction(self) -> Instruction:
        """
        @return: Instruction by iteration number
        """
        return self.instructions[self.iteration]

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

    def load_labels(self):
        """
        Loops through instructions and add labels to the list of labels
        """
        for ins in self.instructions:
            if ins.opcode == 'LABEL':
                self.add_label(Label(ins.arguments[0].value, ins.order))

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
            message = 'Unknown frame opcode: ' + frame_opcode
            print_error_message(message, ERROR_XML_UNEXPECTED_STRUCTURE)

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

    def args_compare(self, arg1, arg2, operation):
        """
        The function compares two arguments
        @param arg1:        First argument
        @param arg2:        Second argument
        @param operation:   Operation e.g. EQ, NEQ, LT, GT
        """
        # Loads arguments into variables and check their initializations
        var1 = self.get_var(arg1)
        var1.init_control()
        var2 = self.get_var(arg2)
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
        # Loads the arguments
        arg1 = self.get_argument(0)
        arg2 = self.get_argument(1)

        # Gets a name of the destination
        dest_name = arg1.value[3:]

        # Checks the existence of the variable
        if not self.get_frame().contain_var(dest_name):
            print_error_message('Attempt in working with non existent variable', ERROR_NON_EXISTENT_VARIABLE)

        # Gets the variable from the second argument
        var = self.get_var(arg2)
        # Control of the initialization
        var.init_control()

        # Rewrites the name and then updates the variable in the frame
        var.set_name(dest_name)
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
        Defines new variable on frame determined by its argument
        """
        # Loads the argument
        arg_val = self.get_argument(0).value
        frame = arg_val[0:2]
        name = arg_val[3:]

        # Checks redefinition of the variable
        if self.get_frame().contain_var(name):
            print_error_message('Redefinition of the variable in push on frame: ' + frame, ERROR_SEMANTIC_CONTROL)
        else:
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
        arg1 = self.get_argument(0)

        var = self.get_var(arg1)

        self.stack.push(var)

    def ins_pops(self):
        """
        Pops the variable from the stack
        """
        # Loads the first argument
        arg1 = self.get_argument(0)

        # Translates the argument into a variable
        var = self.get_var(arg1)

        # Gets the variable from the stack
        var_from_stack = self.stack.pop()

        # Rewrites its name
        var_from_stack.set_name(var.name)

        # Updates the variable on the frame
        self.get_frame().update_var(var_from_stack)

    def math_operation(self, operation):
        """
        The function solves mathematical problem determined by @var operation
        @param operation: Mathematical operation
        """
        # The destination of the argument
        arg1 = self.get_argument(0)

        # Arguments that contains numbers
        arg2 = self.get_argument(1)
        arg3 = self.get_argument(2)

        # Loads arguments into variables
        # The control of the initialization of the second and third argument
        var_return = self.get_var(arg1)
        var_num1 = self.get_var(arg2)
        var_num1.init_control()
        var_num2 = self.get_var(arg3)
        var_num2.init_control()

        # Operation can be called only by INTs types
        if var_num1.type is not Type.INT or var_num2.type is not Type.INT:
            print_error_message('Wrong type\nFunction: math_operation', ERROR_SEMANTIC_CONTROL)

        # Sets the type of the returned variable
        var_return.type = Type.INT

        # Process mathematical operation
        result = 0
        if operation == '+':
            # Addition
            result = var_num1.get_value() + var_num2.get_value()
        elif operation == '-':
            # Substitution
            result = var_num1.get_value() - var_num2.get_value()
        elif operation == '*':
            # Multiplication
            result = var_num1.get_value() * var_num2.get_value()
        elif operation == '//':
            # Division
            if var_num2.get_value() == 0:
                print_error_message('Division by zero', ERROR_WRONG_OPERAND_VALUE)

            result = var_num1.get_value() // var_num2.get_value()
        else:
            # Unknown operator raises error
            print_error_message('Wrong operation\nFunction: math_operation', ERROR_INTERNAL)

        # Updates the var attributes
        var_return.value = result
        var_return.is_init = True

        # Updates variable
        self.get_frame().update_var(var_return)

    def ins_add(self):
        """
        Addition
        """
        self.math_operation('+')

    def ins_sub(self):
        """
        Substitution
        """
        self.math_operation('-')

    def ins_mul(self):
        """
        Multiplication
        """
        self.math_operation('*')

    def ins_idiv(self):
        """
        Division
        """
        self.math_operation('//')

    def lt_gt_eq(self, op):
        """
        Loads arguments, performs operation between the second and third and the result will be saved to the first one
        """
        # Destination variable
        arg1 = self.get_argument(0)

        # Operation variables
        arg2 = self.get_argument(1)
        arg3 = self.get_argument(2)

        # Loads first variable, sets properties
        var = self.get_var(arg1)
        var.type = Type.BOOLEAN
        var.is_init = True

        # Sets value
        var.value = True if self.args_compare(arg2, arg3, op) else False

        # Updates the variable in the frame
        self.get_frame().update_var(var)

    def ins_lt(self):
        self.lt_gt_eq('<')

    def ins_gt(self):
        self.lt_gt_eq('>')

    def ins_eq(self):
        self.lt_gt_eq('==')

    def and_or_not(self, op):
        """
        The function performs operation between the arguments
        @param op: Operation
        """
        arg1 = self.get_argument(0)
        arg2 = self.get_argument(1)

        # Sets properties of the result variable
        var_res = self.get_var(arg1)
        var_res.type = Type.BOOLEAN
        var_res.is_init = True

        var1 = self.get_var(arg2)

        # Checks the validity of the variable's type
        if var1.type is not Type.BOOLEAN:
            print_error_message('Wrong operands types\nInstruction: AND or OR or NOT', ERROR_WRONG_OPERANDS)

        # Performs logical operation
        if op == 'and' or op == 'or':
            # AND, OR logical operation
            # Loads a new variable
            arg3 = self.get_argument(2)
            var2 = self.get_var(arg3)

            # Checks the type of the new variable
            if var2.type is not Type.BOOLEAN:
                print_error_message('Wrong operands types\nInstruction: AND or OR', ERROR_WRONG_OPERANDS)

            if op == 'and':
                # AND
                var_res.value = var1.value and var2.value
            else:
                # OR
                var_res.value = var1.value or var2.value
        else:
            # NOT
            var_res.value = not var1.value

        self.get_frame().update_var(var_res)

    def ins_and(self):
        self.and_or_not('and')

    def ins_or(self):
        self.and_or_not('or')

    def ins_not(self):
        self.and_or_not('not')

    def ins_int2char(self):
        """
        Translates int to the char value
        """
        arg1 = self.get_argument(0)
        arg2 = self.get_argument(1)

        end_var = self.get_var(arg1)
        input_var = self.get_var(arg2)

        # Transforms int to the char and catches errors TypeError and ValueError
        char = None
        try:
            char = chr(input_var.value)
        except TypeError:
            print_error_message('Wrong type input\nInstruction: INT2CHAR', ERROR_WORKING_WITH_STRING)
        except ValueError:
            print_error_message('Value error\nInstruction: INT2CHAR', ERROR_WORKING_WITH_STRING)

        # Set attributes of the end_var
        end_var.type = Type.STRING
        end_var.set_value(char)
        end_var.is_init = True

        self.get_frame().update_var(end_var)

    def ins_stri2int(self):
        var_destination = self.get_var(self.get_argument(0))

        var_string = self.get_var(self.get_argument(1))
        var_string.init_control()
        var_int = self.get_var(self.get_argument(2))
        var_int.init_control()

        if var_string.type is not Type.STRING or var_int.type is not Type.INT:
            print_error_message('Incompatible types\nInstruction: STRI2INT', ERROR_WRONG_OPERANDS)

        if len(var_string.value) <= var_int.value:
            print_error_message('Index outside string\nInstruction: STRI2INT', ERROR_WORKING_WITH_STRING)

        result_value = ord(var_string.value[var_int.value])

        result_variable = Variable(var_destination.name, 'int', result_value)

        self.get_frame().update_var(result_variable)

    def ins_read(self):
        """
        Reads from input file and then saves the value to the variable
        """
        arg1 = self.get_argument(0)
        arg2 = self.get_argument(1)

        var1 = self.get_var(arg1)

        # Gets input value and removes it from the input_lines list
        input_value = self.input_lines[0]
        del self.input_lines[0]

        # Updates the attributes of the variable
        var1.set_type(arg2.value)
        var1.set_value(input_value)
        var1.is_init = True

        self.get_frame().update_var(var1)

    def ins_write(self):
        """
        The function prints the argument to the stdout
        """
        arg = self.get_argument(0)

        # Gets variable from the argument and then checks its initialization
        var = self.get_var(arg)
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
        dest = self.get_argument(0)

        arg1 = self.get_argument(1)
        arg2 = self.get_argument(2)

        # Checks initialization of the variables
        var1 = self.get_var(arg1)
        var1.init_control()
        var2 = self.get_var(arg2)
        var2.init_control()

        # Checks the types of the variables
        if var1.type is not Type.STRING or var2.type is not Type.STRING:
            print_error_message('Not allowed type\nInstruction: CONCAT', ERROR_SEMANTIC_CONTROL)

        # Gets the name of the first argument variable
        dest_name = dest.value[3:]

        # Updates the attributes of the variable
        var1.set_name(dest_name)
        var1.set_value(var1.get_value() + var2.get_value())

        self.get_frame().update_var(var1)

    def ins_strlen(self):
        var1 = self.get_var(self.get_argument(0))
        var2 = self.get_var(self.get_argument(1))
        var2.init_control()

        if var2.type is not Type.STRING:
            print_error_message('Wrong operand type\nInstruction: STRLEN', ERROR_WRONG_OPERANDS)

        result_value = len(var2.value)

        result_variable = Variable(var1.name, 'int', result_value)

        self.get_frame().update_var(result_variable)

    def ins_getchar(self):
        var1 = self.get_var(self.get_argument(0))
        var2 = self.get_var(self.get_argument(1))
        var2.init_control()
        var3 = self.get_var(self.get_argument(2))
        var3.init_control()

        if var2.type is not Type.STRING or var3.type is not Type.INT:
            print_error_message('Wrong operand type\nInstruction: GETCHAR', ERROR_WRONG_OPERANDS)

        if len(var2.value) <= var3.value:
            print_error_message('Index outside string\nInstruction: GETCHAR', ERROR_WORKING_WITH_STRING)

        result_value = var2.value[var3.value]

        result_variable = Variable(var1.name, 'string', result_value)

        self.get_frame().update_var(result_variable)

    def ins_setchar(self):
        var1 = self.get_var(self.get_argument(0))
        var1.init_control()
        var2 = self.get_var(self.get_argument(1))
        var2.init_control()
        var3 = self.get_var(self.get_argument(2))
        var3.init_control()

        if var1.type is not Type.STRING or var2.type is not Type.INT or var3.type is not Type.STRING:
            print_error_message('Wrong operand type\nInstruction: SETCHAR', ERROR_WRONG_OPERANDS)

        var1.value[var2.value] = var3.value[0]

        self.get_frame().update_var(var1)

    def ins_type(self):
        var1 = self.get_var(self.get_argument(0))
        var2 = self.get_var(self.get_argument(1))

        result_value = ''
        if var2.type is Type.STRING:
            result_value = 'string'
        elif var2.type is Type.INT:
            result_value = 'int'
        elif var2.type is Type.BOOLEAN:
            result_value = 'bool'
        elif var2.type is Type.NULL:
            result_value = 'nil'

        result_variable = Variable(var1.name, 'string', result_value)
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

        arg2 = self.get_argument(1)
        arg3 = self.get_argument(2)

        if self.args_compare(arg2, arg3, '=='):
            self.iteration = label.order - 1

    def ins_jumpifneq(self):
        """
        Jumps to the label if the second and third arguments are not equal
        """
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]

        label: Label = self.get_label(arg1.value)

        arg2 = instruct.arguments[1]
        arg3 = instruct.arguments[2]

        if self.args_compare(arg2, arg3, '!='):
            self.iteration = label.order - 1

    def ins_exit(self):
        var = self.get_var(self.get_argument(0))

        if var.type is not Type.INT:
            print_error_message('Wrong operand type\nInstruction: EXIT', ERROR_WRONG_OPERANDS)

        if not 0 <= var.value <= 49:
            print_error_message('Exit code outside allowed range\nInstruction: EXIT', ERROR_WRONG_OPERAND_VALUE)

        exit(var.value)

    def ins_dprint(self):
        var = self.get_var(self.get_argument(0))
        sys.stderr.write(str(translate_to_normal_string(var.value)) + '\n')

    def ins_break(self):
        sys.stderr.write('The iteration number: ' + str(self.iteration) + '\n')
        sys.stderr.write('The number of the proceeded functions: ' + str(self.number_of_proceeded_functions) + '\n\n')
        self.frames.print_frames_to_stderr()

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

            # Load numbers
            num1 = source_string[index + 1]
            num2 = source_string[index + 2]
            num3 = source_string[index + 3]

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
            message = 'Unknown parameter: ' + arg
            print_error_message(message, ERROR_INVALID_PARAMS_COMBINATION)

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
        print_error_message('Language of source file has to be \'IPPcode22\'', ERROR_XML_NOT_WELL_FORMED)

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
        my_program.call_function(my_program.get_instructions()[my_program.iteration].opcode)


# The calling of the main function
if __name__ == "__main__":
    main()
