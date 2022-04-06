# -----------------------------------------------------------------------------
# PROJECT 	:		Interpreter IPP 2022
# FILE 		:		interpret.py
# EMAIL		:		xdzuri00@stud.fit.vutbr.cz
# AUTHOR 	:		Adam Dzurilla, xdzuri00
# -----------------------------------------------------------------------------

# NOTES
# STDIN = sys.stdin

import sys
import xml.etree.ElementTree as ET

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


class Program:
    def __init__(self):
        self.labels = []
        self.instructions = []
        self.stack = Stack()

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

        self.instructions.append(instruction)
        if instruction.opcode == 'LABEL':
            self.add_label(Label(instruction.arguments[0].value))

        self.sort_instructions()

    def sort_instructions(self):
        self.instructions.sort(key=Instruction.get_order)

    def get_instructions(self):
        return self.instructions

    def get_labels(self):
        return self.labels

    def ins_move(self):
        pass

    def ins_createframe(self):
        pass

    def ins_pushframe(self):
        pass

    def ins_popframe(self):
        pass

    def ins_defvar(self):
        pass

    def ins_call(self):
        pass

    def ins_return(self):
        pass

    def ins_pushs(self):
        pass

    def ins_pops(self):
        pass

    def ins_add(self):
        pass

    def ins_sub(self):
        pass

    def ins_mul(self):
        pass

    def ins_idiv(self):
        pass

    def ins_lt(self):
        pass

    def ins_gt(self):
        pass

    def ins_eq(self):
        pass

    def ins_and(self):
        pass

    def ins_or(self):
        pass

    def ins_not(self):
        pass

    def ins_int2char(self):
        pass

    def ins_stri2int(self):
        pass

    def ins_read(self):
        pass

    def ins_write(self):
        pass

    def ins_concat(self):
        pass

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
        pass

    def ins_jumpifeq(self):
        pass

    def ins_jumpifneq(self):
        pass

    def ins_exit(self):
        pass

    def ins_dprint(self):
        pass

    def ins_break(self):
        pass


class Instruction:
    """
	Class store instruction variables
	"""

    def __init__(self, order, opcode, arguments):
        self.order = int(order)
        self.opcode = opcode
        self.arguments = arguments
        if self.order < 1:
            print_error_message('Invalid instruction order number', ERROR_XML_NOT_WELL_FORMED)

    def get_order(self):
        return self.order


class Argument:
    """
	Class store argument values
	"""

    def __init__(self, arg_type, value):
        self.type = arg_type
        self.value = value


class Stack:
    def __init__(self):
        """
		Stack preserve frames with variables
		"""
        self.global_frame = Frame()
        self.local_frames = []
        self.local_frame = None
        self.temporary_frame = None

    def move_temporary_frame_to_stack(self):
        """
		Function add temporary frame at beginning of frames list
		:return:
		"""
        self.local_frames = self.temporary_frame + self.local_frames
        self.temporary_frame = None

    def define_tf(self):
        self.temporary_frame = Frame()


class Frame:
    """
	Class store variables in list and could manipulate with them
	"""

    def __init__(self):
        self.variables = []

    def add(self, variable):
        self.variables += variable

    def remove(self, variable):
        self.variables.remove(variable)


class Variable:
    """
	Class store variable value and if is it initialized
	"""

    def __init__(self, name, value, is_init=False):
        self.name = name
        self.value = value
        self.isInit = is_init


class Label:
    def __init__(self, name):
        self.name = name


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

    return source_file, input_file


def load_xml(tree, program):
    """
	Function gets xml file and iterate through it to get instructions and their arguments
	:param tree:	tree of xml file
	:param program:		Program structure where instructions will be added
	:return:
	"""
    root = tree.getroot()
    for instruct in root:
        if instruct.tag != 'instruction':
            print_error_message('Unexpected element', ERROR_XML_UNEXPECTED_STRUCTURE)
        arguments = []
        for arg in instruct:
            arguments.append(Argument(arg.attrib['type'], arg.text))
        program.add_instruction(
            Instruction(
                instruct.attrib['order'],
                instruct.attrib['opcode'].upper(),
                arguments
            )
        )


def main():
    """
	Main program function
	:return:
	"""
    arguments = sys.argv    # Load arguments into variable
    arguments.pop(0)    # Remove 'interpret.py' parameter from list
    source_file, input_file = check_arguments(arguments)    # Check parameters validation

    tree = None
    try:
        tree = ET.parse(source_file)
    except FileNotFoundError:
        print_error_message('File was not found', ERROR_OPEN_INPUT_FILE)
    except PermissionError:
        print_error_message('Permission denied in opening file', ERROR_OPEN_INPUT_FILE)
    except (ET.ParseError, OSError):
        print_error_message('Fail in work with source_file', ERROR_OPEN_INPUT_FILE)

    my_program = Program()
    load_xml(tree, my_program)


# main function calling
if __name__ == "__main__":
    main()
