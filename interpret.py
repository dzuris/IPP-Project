# -----------------------------------------------------------------------------
# PROJECT 	:		Interpreter IPP 2022
# FILE 		:		interpret.py
# EMAIL		:		xdzuri00@stud.fit.vutbr.cz
# AUTHOR 	:		Adam Dzurilla, xdzuri00
# -----------------------------------------------------------------------------

# TODO: Interpretacia

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
	Function prints error message on stderr (Standard error output)
	:param message:		Gets message which will be printed on stderr
	:param error_code:	Function exits with this error_code
	"""
    sys.stderr.write('ERROR: ' + message + '\n')
    exit(error_code)


def print_help_message():
    """
	This function prints help message for user
	It should make program easier to use
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
    UNINITIALIZED = 0
    STRING = 1
    INT = 2
    BOOLEAN = 3
    NULL = 4


class Label:
    def __init__(self, name, order):
        self.name = name
        self.order = order


class Instruction:
    """
	Class store instruction variables
	"""

    def __init__(self, order: int, opcode: str, arguments):
        self.order = order
        self.opcode = opcode
        self.arguments = arguments
        if self.order < 1:
            print_error_message('Invalid instruction order number', ERROR_XML_UNEXPECTED_STRUCTURE)

    def get_order(self):
        return self.order


class Argument:
    """
	Class store argument values
	"""

    def __init__(self, arg_type, value):
        self.type: str = arg_type
        self.value = '' if value is None else value


class Variable:
    """
	Class store variable value and if is it initialized
	"""

    def __init__(self, variable_name, variable_type=None, variable_value=None):
        self.name = variable_name
        self.type = Type.UNINITIALIZED
        self.value = variable_value

        if variable_type is not None:
            self.set_type(variable_type)
            self.set_value(variable_value)
        self.isInit = False if self.type is Type.UNINITIALIZED else True

    def set_name(self, name):
        self.name = name

    def set_type(self, var_type: str):
        if var_type == 'string':
            self.type = Type.STRING
        elif var_type == 'int':
            self.type = Type.INT
        elif var_type == 'bool':
            self.type = Type.BOOLEAN
        elif var_type == 'nil':
            self.type = Type.NULL
        else:
            message = 'Unknown type value: ' + str(var_type)
            print_error_message(message, ERROR_XML_UNEXPECTED_STRUCTURE)

    def set_value(self, value):
        if self.type is Type.STRING:
            self.value = str(value)
        elif self.type is Type.INT:
            self.value = int(value)
        elif self.type is Type.BOOLEAN:
            self.value = value == 'true'
        elif self.type is Type.NULL:
            self.value = None
        else:
            print_error_message('Program bad processed variable type. Class Variable, function set_value',
                                ERROR_INTERNAL)

    def get_value(self):
        return self.value

    def init_control(self):
        if self.isInit is False:
            print_error_message('Uninitialized variable: ' + self.name, ERROR_SEMANTIC_CONTROL)


class Frame:
    """
	Class store list of variables and could manipulate with them
	"""

    def __init__(self):
        self.variables = []

    def add(self, variable: Variable):
        for var in self.variables:
            if var.name == variable.name:
                print_error_message('Variable redefinition', ERROR_SEMANTIC_CONTROL)

        self.variables.append(variable)

    def remove(self, variable: Variable):
        self.variables.remove(variable)

    def contain_var(self, var_name: str):
        for var in self.variables:
            if var.name == var_name:
                return True

        return False

    def get_variable(self, var_name: str):
        for var in self.variables:
            if var.name == var_name:
                return var

        print_error_message('Undefined variable: ' + var_name, ERROR_NON_EXISTENT_VARIABLE)

    def update_var(self, variable: Variable):
        self.remove(self.get_variable(variable.name))
        self.add(variable)


class Frames:
    def __init__(self):
        """
		Stack preserve frames with variables
		"""
        self.global_frame = Frame()
        self.local_frames = []
        self.local_frame = None
        self.temporary_frame = None

    def create_tf(self):
        self.temporary_frame = Frame()

    def push_frame(self):
        if self.temporary_frame is None:
            print_error_message('Undefined frame\nInstruction: PUSHFRAME', ERROR_NON_EXISTENT_FRAME)

        self.local_frames.append(self.temporary_frame)
        self.local_frame = self.temporary_frame
        self.temporary_frame = None

    def pop_frame(self):
        if not self.local_frames:
            print_error_message('No local frame\nInstruction: POPFRAME', ERROR_NON_EXISTENT_FRAME)

        self.temporary_frame = self.local_frames.pop()


class Stack:
    def __init__(self):
        self.list = []

    def push(self, value):
        self.list.append(value)

    def pop(self):
        if self.list:
            return self.list.pop()
        else:
            print_error_message('Pop from empty stack', ERROR_MISSING_VALUE)


class Program:
    def __init__(self, input_lines):
        self.iteration = 0
        self.instructions = []
        self.labels = []
        self.frames = Frames()
        self.input_lines = input_lines
        self.stack = Stack()
        self.stack_calls = Stack()

    def add_label(self, label):
        if label in self.labels:
            print_error_message('Label redefinition', ERROR_SEMANTIC_CONTROL)
        else:
            self.labels.append(label)

    def add_instruction(self, instruction):
        valid_instructions = ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN',
                              'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT',
                              'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT', 'STRLEN', 'GETCHAR', 'SETCHAR',
                              'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK']

        if instruction.opcode not in valid_instructions:
            print_error_message('Invalid instruction opcode', ERROR_XML_UNEXPECTED_STRUCTURE)

        for ins in self.instructions:
            if ins.order == instruction.order:
                print_error_message('Duplicate instruction order', ERROR_XML_UNEXPECTED_STRUCTURE)

        self.instructions.append(instruction)

    def sort_instructions(self):
        self.instructions.sort(key=Instruction.get_order)
        rewrite_order = 1
        for ins in self.instructions:
            ins.order = rewrite_order
            rewrite_order += 1

    def get_instructions(self):
        return self.instructions

    def get_instruction(self):
        return self.instructions[self.iteration]

    def load_labels(self):
        for ins in self.instructions:
            if ins.opcode == 'LABEL':
                self.add_label(Label(ins.arguments[0].value, ins.order))

    def get_label(self, label_name: str):
        labels = self.labels
        for label in labels:
            if label.name == label_name:
                return label

        print_error_message('Undefined label', ERROR_SEMANTIC_CONTROL)

    def get_frame(self, frame_opcode: str):
        if frame_opcode == 'GF':
            return self.frames.global_frame
        elif frame_opcode == 'LF':
            if self.frames.local_frame is None:
                print_error_message('Local frame does not exists', ERROR_NON_EXISTENT_FRAME)
            else:
                return self.frames.local_frame
        elif frame_opcode == 'TF':
            if self.frames.temporary_frame is None:
                print_error_message('Temporary frame does not exists', ERROR_NON_EXISTENT_FRAME)
            else:
                return self.frames.temporary_frame
        else:
            message = 'Unknown frame opcode: ' + frame_opcode
            print_error_message(message, ERROR_XML_UNEXPECTED_STRUCTURE)

    def get_var(self, argument: Argument):
        if argument.type == 'var':
            frame = argument.value[0:2]
            name = argument.value[3:]
            var = self.get_frame(frame).get_variable(name)
        else:
            var = Variable(None, argument.type, argument.value)

        return var

    def is_iteration_end(self):
        return self.iteration == len(self.instructions)

    def args_compare(self, arg1, arg2, operation):
        var1 = self.get_var(arg1)
        var1.init_control()
        var2 = self.get_var(arg2)
        var2.init_control()

        # Now we have loaded our two variables in var1 and var2
        if var1.type != var2.type:
            print_error_message('Different types in comparison\nFunction: arguments_comparison', ERROR_WRONG_OPERANDS)

        if operation == '==':
            return True if var1.value == var2.value else False
        elif operation == '!=':
            return True if var1.value != var2.value else False
        elif operation == '>':
            return True if var1.value > var2.value else False
        elif operation == '<':
            return True if var1.value < var2.value else False
        else:
            print_error_message('Unknown operator\nFunction: arguments_comparison', ERROR_INTERNAL)

    def call_function(self, function_opcode: str):
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
            error_message = 'Unknown instruction ' + function_opcode
            print_error_message(error_message, ERROR_XML_UNEXPECTED_STRUCTURE)
        self.iteration += 1

    # region Instructions
    def ins_move(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]
        arg2 = instruct.arguments[1]

        target_frame = arg1.value[0:2]
        target_var_name = arg1.value[3:]
        if not self.get_frame(target_frame).contain_var(target_var_name):
            print_error_message('Attempt in working with non existent variable', ERROR_NON_EXISTENT_VARIABLE)

        var = self.get_var(arg2)
        var.init_control()
        var.set_name(target_var_name)

        self.get_frame(target_frame).update_var(var)

    def ins_createframe(self):
        self.frames.create_tf()

    def ins_pushframe(self):
        self.frames.push_frame()

    def ins_popframe(self):
        self.frames.pop_frame()

    def ins_defvar(self):
        instruct = self.get_instruction()
        frame = instruct.arguments[0].value[0:2]
        name = instruct.arguments[0].value[3:]

        if self.get_frame(frame).contain_var(name):
            print_error_message('Variable redefinition in push on frame: ' + frame, ERROR_SEMANTIC_CONTROL)
        else:
            self.get_frame(frame).add(Variable(name))

    def ins_call(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]

        label = self.get_label(arg1.value)

        self.stack_calls.push(self.iteration + 1)
        self.iteration = label.order - 1

    def ins_return(self):
        self.iteration = self.stack_calls.pop()

    def ins_pushs(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]

        var = self.get_var(arg1)

        self.stack.push(var)

    def ins_pops(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]

        var = self.get_var(arg1)
        var_from_stack = self.stack.pop()

        var_from_stack.set_name(var.name)

        frame = arg1.value[0:2]

        self.get_frame(frame).update_var(var_from_stack)

    def math_operation(self, operation):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]
        arg2 = instruct.arguments[1]
        arg3 = instruct.arguments[2]

        var1 = self.get_var(arg1)
        var2 = self.get_var(arg2)
        var2.init_control()
        var3 = self.get_var(arg3)
        var3.init_control()

        if var2.type is not Type.INT or var3.type is not Type.INT:
            print_error_message('Wrong type\nInstruction: ADD', ERROR_SEMANTIC_CONTROL)

        var1.type = Type.INT

        if operation == '+':
            res = var2.get_value() + var3.get_value()
        elif operation == '-':
            res = var2.get_value() - var3.get_value()
        elif operation == '*':
            res = var2.get_value() * var3.get_value()
        else:
            if var3.get_value() == 0:
                print_error_message('Attempt divide by zero', ERROR_WRONG_OPERAND_VALUE)

            res = var2.get_value() // var3.get_value()

        var1.value = res
        var1.isInit = True

        self.get_frame(arg1.value[0:2]).update_var(var1)

    def ins_add(self):
        self.math_operation('+')

    def ins_sub(self):
        self.math_operation('-')

    def ins_mul(self):
        self.math_operation('*')

    def ins_idiv(self):
        self.math_operation('//')

    def lt_gt_eq(self, op):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]
        arg2 = instruct.arguments[1]
        arg3 = instruct.arguments[2]

        var = self.get_var(arg1)
        var.type = Type.BOOLEAN
        var.isInit = True

        var.value = True if self.args_compare(arg2, arg3, op) else False

    def ins_lt(self):
        self.lt_gt_eq('<')

    def ins_gt(self):
        self.lt_gt_eq('>')

    def ins_eq(self):
        self.lt_gt_eq('==')

    def ins_and(self):
        pass

    def ins_or(self):
        pass

    def ins_not(self):
        pass

    def ins_int2char(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]
        arg2 = instruct.arguments[1]

        end_var = self.get_var(arg1)
        input_var = self.get_var(arg2)

        char = None
        try:
            char = chr(input_var.value)
        except TypeError:
            print_error_message('Wrong type input\nInstruction: INT2CHAR', ERROR_WORKING_WITH_STRING)
        except ValueError:
            print_error_message('Value error\nInstruction: INT2CHAR', ERROR_WORKING_WITH_STRING)

        if end_var.type is Type.UNINITIALIZED:
            end_var.type = Type.STRING
            end_var.set_value(char)
            end_var.isInit = True

        if end_var.type is not Type.STRING:
            print_error_message('Wrong destination variable type\nInstruction: INT2CHAR', ERROR_SEMANTIC_CONTROL)

        frame = arg1.value[0:2]

        self.get_frame(frame).update_var(end_var)

    def ins_stri2int(self):
        pass

    def ins_read(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]
        arg2 = instruct.arguments[1]

        var1 = self.get_var(arg1)
        input_value = self.input_lines[0]
        del self.input_lines[0]

        var1.set_type(arg2.value)
        var1.set_value(input_value)
        var1.isInit = True

        self.get_frame(arg1.value[0:2]).update_var(var1)

    def ins_write(self):
        instruct = self.get_instruction()
        arg = instruct.arguments[0]

        var = self.get_var(arg)
        var.init_control()

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
        instruct = self.get_instruction()
        dest = instruct.arguments[0]
        arg1 = instruct.arguments[1]
        arg2 = instruct.arguments[2]

        var1 = self.get_var(arg1)
        var1.init_control()
        var2 = self.get_var(arg2)
        var2.init_control()

        if var1.type is not Type.STRING or var2.type is not Type.STRING:
            print_error_message('Not allowed type. Instruction CONCAT', ERROR_SEMANTIC_CONTROL)

        dest_frame = dest.value[0:2]
        dest_name = dest.value[3:]

        var1.set_name(dest_name)
        var1.set_value(var1.get_value() + var2.get_value())

        self.get_frame(dest_frame).update_var(var1)

    def ins_strlen(self):
        pass

    def ins_getchar(self):
        pass

    def ins_setchar(self):
        pass

    def ins_type(self):
        pass

    def ins_label(self):
        pass

    def ins_jump(self):
        instruct = self.get_instruction()
        arg = instruct.arguments[0]
        label = self.get_label(arg.value)
        self.iteration = label.order - 1

    def ins_jumpifeq(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]

        label: Label = self.get_label(arg1.value)

        arg2 = instruct.arguments[1]
        arg3 = instruct.arguments[2]

        if self.args_compare(arg2, arg3, '=='):
            self.iteration = label.order - 1

    def ins_jumpifneq(self):
        instruct = self.get_instruction()
        arg1 = instruct.arguments[0]

        label: Label = self.get_label(arg1.value)

        arg2 = instruct.arguments[1]
        arg3 = instruct.arguments[2]

        if self.args_compare(arg2, arg3, '!='):
            self.iteration = label.order - 1

    def ins_exit(self):
        pass

    def ins_dprint(self):
        pass

    def ins_break(self):
        pass
    # endregion


def translate_to_normal_string(source_string: str):
    final = ''
    skip = 0
    for index in range(len(source_string)):
        if skip != 0:
            skip -= 1
            continue

        char = source_string[index]
        if char == '\\':
            num = 100 * int(source_string[index + 1]) + 10 * int(source_string[index + 2]) + int(
                source_string[index + 3])
            final += chr(num)
            skip = 3
        elif char == '&':
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
	Program checks each argument and if there is forbidden combination, then print error message
	and exit program with appropriate exit code
	:param arguments:	List of arguments which are checked in cycle
	:return:
		Source file, if it's not choose by parameter then it's read from stdin
		Input file, if it's not choose by parameter then it's read from stdin
	"""
    source_file = None
    input_file = None
    for arg in arguments:
        if arg == '--help':
            if len(sys.argv) != 1:
                print_error_message('--help param can\'t be used with other parameters',
                                    ERROR_INVALID_PARAMS_COMBINATION)
            else:
                print_help_message()
        elif arg[0:9] == '--source=':
            source_file = arg[9:]
        elif arg[0:8] == '--input=':
            input_file = arg[8:]
        else:
            message = 'Unknown parameter: ' + arg
            print_error_message(message, ERROR_INVALID_PARAMS_COMBINATION)

    if source_file is None:
        source_file = sys.stdin

    if input_file is None:
        input_file = sys.stdin
    else:
        f = open(input_file, 'r')
        input_file = f.read().splitlines()

    return source_file, input_file


def load_xml(tree, program):
    """
	Function gets xml file and iterate through it to get instructions and their arguments
	:param tree:	tree of xml file
	:param program:		Program structure where instructions will be added
	:return:
	"""
    root = tree.getroot()
    if root.attrib['language'] != 'IPPcode22':
        print_error_message('Language of source file has to be \'IPPcode22\'', ERROR_XML_NOT_WELL_FORMED)

    for instruct in root:
        if instruct.tag != 'instruction':
            print_error_message('Unexpected element', ERROR_XML_UNEXPECTED_STRUCTURE)
        arguments = []
        for arg in instruct:
            arguments.append(Argument(arg.attrib['type'], arg.text))
        program.add_instruction(
            Instruction(
                int(instruct.attrib['order']),
                instruct.attrib['opcode'].upper(),
                arguments
            )
        )

    program.sort_instructions()
    program.load_labels()


def main():
    """
	Main program function
	:return:
	"""
    arguments = sys.argv  # Load arguments into variable
    arguments.pop(0)  # Remove 'interpret.py' parameter from list
    source_file, input_lines = check_arguments(arguments)  # Check parameters validation

    tree = None
    try:
        tree = ET.parse(source_file)
    except FileNotFoundError:
        print_error_message('Source file was not found\nFile name: ' + source_file, ERROR_OPEN_INPUT_FILE)
    except PermissionError:
        print_error_message('Permission denied in opening file', ERROR_OPEN_INPUT_FILE)
    except (ET.ParseError, OSError):
        print_error_message('Fail in work with source_file', ERROR_OPEN_INPUT_FILE)

    my_program = Program(input_lines)
    load_xml(tree, my_program)

    # Program interpretation
    while not my_program.is_iteration_end():
        my_program.call_function(my_program.get_instructions()[my_program.iteration].opcode)


# main function calling
if __name__ == "__main__":
    main()
