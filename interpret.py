#-----------------------------------------------------------------------------
# PROJECT 	:		Interpreter IPP 2022
# FILE 		:		interpret.py
# EMAIL		:		xdzuri00@stud.fit.vutbr.cz
# AUTHOR 	:		Adam Dzurilla, xdzuri00
#-----------------------------------------------------------------------------

# NOTES
# STDIN = sys.stdin
# TEST GITHUB 1

import sys
import xml.etree.ElementTree as ET

SOURCE_FILE = ''
INPUT_FILE = ''

ERROR_INVALID_PARAMS_COMBINATION = 10
ERROR_OPEN_INPUT_FILE = 11
ERROR_OPEN_OUTPUT_FILE = 12
ERROR_XML_NOT_WELL_FORMED = 31
ERROR_UNEXPECTED_XML_STRUCTURE = 32
ERROR_SEMANTIC_CONTROL = 52			# Using of undefined label, variable redefinition
ERROR_WRONG_OPERANDS = 53			# Wrong operands types
ERROR_NON_EXISTENT_VARIABLE = 54	# frame exists but variable don't
ERROR_NON_EXISTENT_FRAME = 55		# e.g. reading from empty frame
ERROR_MISSING_VALUE = 56			# in variable, in frame etc.
ERROR_WRONG_OPERAND_VALUE = 57		# e.g. dividing by zero, wrong exit return
ERROR_WORKING_WITH_STRING = 58
ERROR_INTERNAL = 99

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

class Instruction:
	"""
		Class store instruction variables
	"""
	def __init__(self, order, opcode, arguments):
		self.order = order
		self.opcode = opcode
		self.arguments = arguments

class Argument:
	"""
		Class store argument values
	"""
	def __init__(self, arg_type, value):
		self.type = arg_type
		self.value = value

class Variable:
	"""
		Class store variable value and if is it initialized
	"""
	def __init__(self, value, is_init = False):
		self.value = value
		self.isInit = is_init

class Frame:
	def __init__(self):
		self.list = []

	def add(self, variable):
		self.list += variable

	def remove(self, variable):
		self.list.remove(variable)

class Stack:
	def __init__(self, global_frame):
		"""
		Stack preserve frames with variables
		:param global_frame:	Initialization must be called with global frame
		"""
		self.global_frame = global_frame
		self.frames = []
		self.local_frame = None
		self.temporary_frame = None

	def move_temporary_frame_to_stack(self):
		"""
		Function add temporary frame at beginning of frames list
		:return:
		"""
		self.frames = self.temporary_frame + self.frames
		self.temporary_frame = None

	def define_tf(self):
		self.temporary_frame = []

def check_arguments(arguments):
	"""
	Program checks each argument and if there is forbidden combination, then print error message
	and exit program with appropriate exit code
	:param arguments:	List of arguments which are checked in cycle
	:return:
	"""
	global SOURCE_FILE
	global INPUT_FILE
	for arg in arguments:
		if arg == '--help':
			if len(sys.argv) != 1:
				sys.stderr.write('--help param can\'t be used with other parameters\n')
				exit(ERROR_INVALID_PARAMS_COMBINATION)
			else:
				print_help_message()
		elif arg[0:9] == '--source=':
			SOURCE_FILE=arg[9:]
		elif arg[0:8] == '--input=':
			INPUT_FILE=arg[8:]
		else:
			sys.stderr.write('Unknown parameter: ' + arg + '\n')
			exit(ERROR_INVALID_PARAMS_COMBINATION)

def main():
	"""
	Main program function
	:return:
	"""
	arguments = sys.argv			# Load arguments into variable
	arguments.pop(0)				# Remove 'interpret.py' parameter from list
	check_arguments(arguments)		# Check parameters validation
	f = open("test.txt", "r")
	xml_file = f.read()
	print(xml_file)
	#print(SOURCE_FILE)
	#print(INPUT_FILE)

main()
