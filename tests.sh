#!/bin/bash

RED=`tput setaf 1`
GREEN=`tput setaf 2`
ORANGE=`tput setaf 3`
NO_COLOR=`tput sgr0`

output_file="test_file_for_outputs.xml"

test_num=1
print_test_num() {
	echo "Test ${test_num}"
	let "test_num+=1"
}

expect() {
	print_test_num
	command="php8.1 parse.php <${file} >${output_file} 2>&1"
	eval ${command}
	return_code=$?
	if [ $1 -eq ${return_code} ]; then
		echo "${GREEN}Test successfull - return code: ${return_code}"
		echo "File: $2${NO_COLOR}"
	else
		echo "${RED}ERROR"
		echo "Return code: ${return_code}"
		echo "Expected: $1"
		echo "File: $2"
		echo "Command: ${command}${NO_COLOR}"
		exit 1
	fi
}

compare_file() {
	cmp_res="compare_return_result.txt"
	java -jar /pub/courses/ipp/jexamxml/jexamxml.jar $1 ${output_file} diffs.xml  /D /pub/courses/ipp/jexamxml/options >${cmp_res}
	if [ "$(tail -1 ${cmp_res})" == "Two files are identical" ]; then
		echo "${GREEN}Files are identical${NO_COLOR}"
	else
		echo "${RED}Files are different${NO_COLOR}"
		echo "DIFFERENTS:"
		cat diffs.xml
		exit 1
	fi
	echo ""
	rm ${cmp_res}
}

headers_route="tests/headers"
basic_route="tests/basics"
commands_route="tests/commands"
supplementary_route="tests/basics"

header_tests() {
	echo "${ORANGE}HEADER TESTS${NO_COLOR}"

	# Test Header 1
	file="${headers_route}/testHead1.IPPcode22"
	expect 21 $file
	echo ""

	# Test Header 2
	file="${headers_route}/testHead2.IPPcode22"
	expect 0 $file
	echo ""

	# Test Header 3
	file="${headers_route}/testHead3.IPPcode22"
	expect 21 $file
	echo ""

	# Test Header 4
	file="${headers_route}/testHead4.IPPcode22"
	expect 0 $file
	echo ""
}

basic_tests() {
	echo "${ORANGE}BASIC TESTS${NO_COLOR}"

	# Test 1
	file="${basic_route}/test1.IPPcode22"
	expect 0 $file
	compare_file "${basic_route}/test1.xml"
}

commands_tests() {
	echo "${ORANGE}COMMANDS TESTS${NO_COLOR}"

	# Move Command
	file="${commands_route}/test_move.IPPcode22"
	expect 0 $file
	compare_file "${commands_route}/test_move.xml"

	# Frames Commands
	file="${commands_route}/test_frame.IPPcode22"
	expect 0 $file
	compare_file "${commands_route}/test_frame.xml"
}

supplementary_tests() {
	echo "${ORANGE}SUPPLEMENTARY TESTS${NO_COLOR}"

	# Read test
	file="${supplementary_route}/read_test.src"
	expect 0 $file
	compare_file "${supplementary_route}/read_test.out"

	# Simple test
	file="${supplementary_route}/simple_tag.src"
	expect 0 $file
	compare_file "${supplementary_route}/simple_tag.out"

	# Write test
	file="${supplementary_route}/write_test.src"
	expect 0 $file
	compare_file "${supplementary_route}/write_test.out"
}

# MAIN

touch ${output_file}

header_tests
basic_tests
commands_tests
supplementary_tests

echo "${GREEN}ALL FILES RUNNED SUCCESSFULLY${NO_COLOR}"

rm ${output_file}
