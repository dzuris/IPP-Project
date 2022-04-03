import sys

def print_help_message():
	print("Help message")

def check_arguments(arguments):
	for arg in arguments:
		if arg == '--help':
			if len(sys.argv) != 1:
				sys.stderr.write('--help param can\'t be used with other parameters')
				exit(10)
			else:
				print_help_message()
	print(arg[0:9])

def main():
	arguments = sys.argv
	arguments.pop(0)
	#print('Arguments: ' + str(arguments))
	check_arguments(arguments)

main()
