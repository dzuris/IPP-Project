Implementační dokumentace k 1. úloze do IPP 2021/2022
Jméno a příjmení: Adam Dzurilla
Login: xdzuri00

# Parse.php

Parse is compiler from IPPcode22 into xml

## Usage

```bash
php8.1 parse.php [OPTIONAL ARGS]
```

Input file is reading from standard input

## Design philosophy

Parse.php contains functions for printing help message, functions for checking data validity and functions for generating xml output.
Program execution:
1. Check passed arguments, and verify combination of those arguments
2. Check if INPUT_FILE has valid header
3. Printing xml header and program attribute
4. Program starts working in while cycle and looping through lines which are proceeded
5. Printing end of program attribute

## Elaboration of commands processing

1. Remove lines which are empty or composed only from whitespaces, and lines which are only comments
2. Remove comments after code
3. Split line into array by space ' '
4. Get first word from line and use function strtoupper and assign it into $commands variable
5. Find $command by switch if is valid otherwise it's lexical error
6. For every command check arguments count, generate instruction attribute and arguments attributes

## AUTHOR
Adam Dzurilla, xdzuri00
