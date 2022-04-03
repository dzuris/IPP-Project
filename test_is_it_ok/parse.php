<?php
	/*************************************************************************
	 *	PROJECT:	Parser
	 *
	 *	FILE:	parser.php
	 *
	 *	AUTHOR: 	Adam Dzurilla, xdzuri00
	 *
	 */

	ini_set('display_errors', 'stderr');

	/**
	 * @brief		printHelpMessage
	 *						* Prints help message
	 */
	function printHelpMessage() {
		echo "Usage: php8.1 parse.php [options] <InputFileFromSTDIN\n";
		echo "Options:\n";
		echo "\t--help\t\t\tDisplay this message\n";
		echo "\t--source=file\t\tSet source file\n";
		echo "\t--source=\"file\"\t\tSet source route\n";
		echo "\n";
		echo "Exit status:\n";
		echo "\t0\t\t\tif ok,\n";
		echo "\t10\t\t\tmissing parameter (if it's needed) or using forbidden parameters combination,\n";
		echo "\t11\t\t\terror in opening input file (e.g. file doesn't exist or permission denied),\n";
		echo "\t12\t\t\terror in opening output file for writing (e.g. permission denied or error in writing),\n";
		echo "\t21\t\t\tmissing or wrong header in source code in language IPPcode22,\n";
		echo "\t22\t\t\tunknown or another operation code in source code in language IPPcode22\n";
		echo "\t23\t\t\tanother lexical or syntactic error in source code in language IPPcode22\n";
		echo "\t99\t\t\tinternal error (e.g. allocation error),\n";
		echo "\n";
		echo "This is help message for program \"parse.php\"\n";
		echo "Full documentation in file: readme1.md\n";
	}

	/**
	 * @brief		checkHeader
	 *						* Function gets header line and remove comments and trim rest whitespaces
	 *
	 * @param		header		header line which should contain ".IPPcode22" (case insensitive)
	 */
	function checkHeader($header) {
		if ($header) {
			while ($header[0] == '#' || ctype_space($header)) $header = fgets(STDIN);
			if (strpos($header, '#')) $header = substr($header, 0, strpos($header, '#'));
			$header = strtoupper(trim($header));
			if($header == ".IPPCODE22") {
				return;
			}
		}

		error_log("Invalid or missing header in source code in language IPPcode22");
		exit(21);
	}

	/**
	 * @brief 	checkArgCount
	 *						* Function checks if count of array is expected value
	 *
	 * @param		splitted					array of strings of splitted line
	 * @param		expectedCount		our expected count
	 */
	function checkArgCount($splitted, $expectedCount) {
		if (count($splitted) != $expectedCount) {
			error_log("Syntactic error: Unexpected number of arguments");
			exit(22);
		}
	}

	/**
	 * @brief		generateInstructionHead
	 *						* Function generates head of the instruction element
	 *
	 * @param		opcode						operation code value in xml output
	 */
	function generateInstructionHead($opcode) {
		static $instructionOrder = 1;
		echo "\t<instruction order=\"$instructionOrder\" opcode=\"$opcode\">\n";
		$instructionOrder++;
	}

	/**
	 * @brief		generateInstructionEnd
	 *						* Function generates end of the instruction element
	 */
	function generateInstructionEnd() {
		echo "\t</instruction>\n";
	}

	/**
	 * @brief		generateArg
	 *						* Function generates argument by passed parameters
	 *
	 * @param		argNum						serial number of the argument in the instruction
	 * @param		dataType					data type of the value which is passed as third parameter
	 * @param		value							value of passed argument
	 */
	function generateArg($argNum, $dataType, $value) {
		echo "\t\t<arg$argNum type=\"$dataType\">$value</arg$argNum>\n";
	}

	/**
	 * @brief		isDataTypeValid
	 *						* Function checks if data type is valid,
	 *							else function exits with EXIT_CODE and print error message
	 *
	 * @param		dataType					data type which is checked by function
	 */
	function isDataTypeValid($dataType) {
		if ($dataType != 'int' && $dataType != 'bool' && $dataType != 'string' && $dataType != 'nil' && $dataType != 'LF' && $dataType != 'TF' && $dataType != 'GF') {
			error_log("Lexical error: Unknown data type");
			exit(22);
		} else {
			return true;
		}
	}

	/**
	 * @brief		getXmlString
	 *						* Function transfer problem chars
	 *
	 * @param		sentence			input which is transfering into output
	 *
	 * @return	output				sentence where problem chars were transfered into not problem chars
	 */
	function getXmlString($sentence) {
		$output = "";
		for ($i=0; $i < strlen($sentence); $i++) {
			if ($sentence[$i] == '<') {
				$output = $output."&lt;";
			}
			elseif ($sentence[$i] == '>') {
				$output = $output."&gt;";
			}
			elseif ($sentence[$i] == '&') {
				$output = $output."&amp;";
			}
			else {
				$output = $output.$sentence[$i];
			}
		}

		return $output;
	}

	/**
	 * @brief		getDataType
	 *						* Function gets sentence in form e.g. "int@5"
	 *							Function gets substring from begin until '@' symbol, check if
	 *							data type is valid and then returns data type
	 *
	 * @param		sentence					string in form e.g. "int@5", function is working with this string and gets "int"
	 *
	 * @return	valid data type (int, bool, string, nil), getted from sentence from beginning until '@' (excluded)
	 */
	function getDataType($sentence) {
		$dataType = substr($sentence, 0, strpos($sentence, '@'));
		isDataTypeValid($dataType);
		if ($dataType == "LF" || $dataType == "TF" || $dataType == "GF") {
			$dataType = "var";
		}

		return $dataType;
	}

	/**
	 * @brief		getDataValue
	 *						* Function gets sentence in form e.g. "int@5"
	 *							Function gets substring from symbol one after '@' until end
	 *
	 * @param		sentence					string in form e.g. "int@5", function is working with this string and gets "5"
	*
	* @return	data value getted from sentence from '@' (excluded) until end of string
	 */
	function getDataValue($sentence) {
		if (getDataType($sentence) == "var") return $sentence;
		$value = substr($sentence, strpos($sentence, '@')+1);
		return getXmlString($value);
	}

	//************************************************************************************************************
	// MAIN BODY

	/// Check parameters
	$isFirst = true;
	foreach ($argv as $arg) {
		if ($isFirst) {
			$isFirst = false;
			continue;
		}

		// Parameter for printing help message
		if ($arg == "--help") {
			// check if is it only one parameter
			if ($argc != 2) {
				error_log("Invalid parameters combination");
				exit(10);
			}
			printHelpMessage();
			exit(0);
		}
		// Parameter for source file
		elseif (substr($arg, 0, 9) == "--source=") {
			$file = substr($arg, 9);

			// Check if user passed file or route with "--source=" parameter
			if (strlen($file) == 0){
				error_log("Missing file in source parameter");
				exit(10);
			}
		}
		// Invalid or first parameter
		else {
			error_log("Invalid parameter");
			exit(10);
		}
	}

	/// Check header validity
	checkHeader(fgets(STDIN));

	/// Generate xml header and program element
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
	echo "<program language=\"IPPcode22\">\n";

	while($line = fgets(STDIN)) {
		/// Delete line if is it just comment or line is composed only from whitespaces
		if ($line[0] == '#' || ctype_space($line)) {
			continue;
		}

		/// Remove comment after code from line
		$position = strpos($line, '#');
		if ($position) {
			$line = substr($line, 0, $position)."\n";
		}

		/// Split instruction into array
		$splitted = explode(' ', rtrim($line));

		$command = strtoupper($splitted[0]);
		switch ($command) {
			case 'MOVE':
				checkArgCount($splitted, 3);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateInstructionEnd();
				break;

			case 'CREATEFRAME':
				checkArgCount($splitted, 1);
				generateInstructionHead($command);
				generateInstructionEnd();
				break;

			case 'PUSHFRAME':
				checkArgCount($splitted, 1);
				generateInstructionHead($command);
				generateInstructionEnd();
				break;

			case 'POPFRAME':
				checkArgCount($splitted, 1);
				generateInstructionHead($command);
				generateInstructionEnd();
				break;

			case 'DEFVAR':
				if (preg_match("/(LF|GF|TF)@[a-zA-Z#*$][a-zA-Z#&*$0-9]*/", $splitted[1])) {
					checkArgCount($splitted, 2);
					generateInstructionHead($command);
					generateArg(1, "var", $splitted[1]);
					generateInstructionEnd();
				}
				else {
					error_log("Lexical error in instruction: DEFVAR");
					exit(22);
				}
				break;

			case 'CALL':
				checkArgCount($splitted, 2);
				generateInstructionHead($command);
				generateArg(1, "label", $splitted[1]);
				generateInstructionEnd();
				break;

			case 'RETURN':
				checkArgCount($splitted, 1);
				generateInstructionHead($command);
				generateInstructionEnd();
				break;

			case 'PUSHS':
				checkArgCount($splitted, 2);
				generateInstructionHead($command);
				generateArg(1, getDataType($splitted[1]), getDataValue($splitted[1]));
				generateInstructionEnd();
				break;

			case 'POPS':
				checkArgCount($splitted, 2);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateInstructionEnd();
				break;

			case 'ADD':
			case 'SUB':
			case 'MUL':
			case 'IDIV':
				checkArgCount($splitted, 4);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateArg(3, getDataType($splitted[3]), getDataValue($splitted[3]));
				generateInstructionEnd();
				break;

			case 'LT':
			case 'GT':
			case 'EQ':
				checkArgCount($splitted, 4);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateArg(3, getDataType($splitted[3]), getDataValue($splitted[3]));
				generateInstructionEnd();
				break;

			case 'AND':
			case 'OR':
				checkArgCount($splitted, 4);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateArg(3, getDataType($splitted[3]), getDataValue($splitted[3]));
				generateInstructionEnd();
				break;

			case 'NOT':
				checkArgCount($splitted, 3);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateInstructionEnd();
				break;

			case 'INT2CHAR':
				checkArgCount($splitted, 3);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateInstructionEnd();
				break;

			case 'STRI2INT':
				checkArgCount($splitted, 4);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateArg(3, getDataType($splitted[3]), getDataValue($splitted[3]));
				generateInstructionEnd();
				break;

			case 'READ':
				checkArgCount($splitted, 3);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, "type", $splitted[2]);
				generateInstructionEnd();
				break;

			case 'WRITE':
				checkArgCount($splitted, 2);
				generateInstructionHead($command);
				generateArg(1, getDataType($splitted[1]), getDataValue($splitted[1]));
				generateInstructionEnd();
				break;

			case 'CONCAT':
				checkArgCount($splitted, 4);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateArg(3, getDataType($splitted[3]), getDataValue($splitted[3]));
				generateInstructionEnd();
				break;

			case 'STRLEN':
				checkArgCount($splitted, 3);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateInstructionEnd();
				break;

			case 'GETCHAR':
			case 'SETCHAR':
				checkArgCount($splitted, 4);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateArg(3, getDataType($splitted[3]), getDataValue($splitted[3]));
				generateInstructionEnd();
				break;

			case 'TYPE':
				checkArgCount($splitted, 3);
				generateInstructionHead($command);
				generateArg(1, "var", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateInstructionEnd();
				break;

			case 'LABEL':
				checkArgCount($splitted, 2);
				generateInstructionHead($command);
				generateArg(1, "label", $splitted[1]);
				generateInstructionEnd();
				break;

			case 'JUMP':
				checkArgCount($splitted, 2);
				generateInstructionHead($command);
				generateArg(1, "label", $splitted[1]);
				generateInstructionEnd();
				break;

			case 'JUMPIFEQ':
			case 'JUMPIFNEQ':
				checkArgCount($splitted, 4);
				generateInstructionHead($command);
				generateArg(1, "label", $splitted[1]);
				generateArg(2, getDataType($splitted[2]), getDataValue($splitted[2]));
				generateArg(3, getDataType($splitted[3]), getDataValue($splitted[3]));
				generateInstructionEnd();
				break;

			case 'EXIT':
				checkArgCount($splitted, 2);
				generateInstructionHead($command);
				$dataType = getDataType($splitted[1]);
				$value = getDataValue($splitted[1]);
				generateArg(1, $dataType, $value);
				generateInstructionEnd();
				break;

			case 'DPRINT':
				error_log($splitted[1]);
				break;

			case 'BREAK':
				error_log("Break at line: $__LINE__, file: $__FILE__, instruction order: $instructionOrder");
				break;

			default:
				error_log("Lexical error, unknown command");
				exit(22);
				break;
		}
	}

	/// Generate end of program element
	echo "</program>\n";

	exit(0);
?>
