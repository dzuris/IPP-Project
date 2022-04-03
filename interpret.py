import sys

SOURCE_FILE = ''
INPUT_FILE = ''

ERROR_INVALID_PARAMS_COMBINATION = 10

def print_help_message():
	print("Help message test")

def check_arguments(arguments):
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

def main():
	arguments = sys.argv
	arguments.pop(0)
	#print('Arguments: ' + str(arguments))
	check_arguments(arguments)
	print(SOURCE_FILE)
	print(INPUT_FILE)

main()
