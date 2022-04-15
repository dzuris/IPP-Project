<?php
/**
 * @project Testing program for programs parse.php and interpret.py
 * @file test.php
 * @email xdzuri00@stud.fit.vutbr.cz
 * @author Adam Dzurilla
 */

// ERROR CODES
const NO_ERROR = 0;
const ERROR_PARAMETERS = 10; // missing parameter or forbidden combination of the parameters
const ERROR_NON_EXISTENT_FILE_IN_PARAM = 41;    // directory, parser, interpreter, jexamxml
const ERROR_INTERN = 99; // Internal error

// FUNCTIONS
/**
 * @param string $message Brief error message
 * @param int $error_code Error return code
 * @return void
 */
function printErrorMessage(string $message, int $error_code): void {
    error_log($message);
    exit($error_code);
}

/**
 * @brief Prints help message for the program
 * @return void
 */
function printHelpMessage(): void {
    echo "Usage:\n";
    echo "\tphp8.1 test.php [OPTIONS]\n\n";

    echo "Options:\n";
    echo "\t--help\t\t\tDisplay this message\n";
    echo "\t--directory=PATH\tSet directory with tests\n";
    echo "\t--recursive\t\tSet if program will check subdirectories in the directory with tests\n";
    echo "\t--parse-script=FILE\tSet parser file\n";
    echo "\t--int-script=FILE\tSet interpreter file\n";
    echo "\t--parse-only\t\tControl only parser\n";
    echo "\t--int-only\t\tControl only interpreter\n";
    echo "\t--jexampath=PATH\tSet jexamxml.jar file for parser controls\n\n";

    echo "Exit status:\n";
    echo "\t0\t\tOK,\n";

    echo "\t10\t\tInvalid combination of the parameters,\n";
    echo "\t11\t\tError in opening input file,\n";
    echo "\t12\t\tError in opening output file,\n";

    echo "\t41\t\tError in opening file from parameter,\n";

    echo "\t99\t\tError internal (e.g. memory allocation)\n\n";

    echo "This is help message for the program \"test.php\"\n";
    echo "For the full documentation see: readme2.md\n";

    exit(NO_ERROR);
}

/**
 * @brief Find if any element in array starts with $preString
 * @param string $preString expected start of the string
 * @param array $array string values
 * @return bool if some string from the array starts with pre string
 */
function preStringInArray(string $preString, array $array): bool
{
    foreach ($array as $i) {
        if (str_starts_with($i, $preString)) {
            return true;
        }
    }

    return false;
}

/**
 * @brief Get names with paths of all the valid files
 * @param string $dirName Directory with tests and subdirectories
 * @return array list of files
 */
function getFiles(string $dirName): array {
    // Check if directory exists
    if (!file_exists($dirName)) {
        printErrorMessage("Fail in opening directory with tests", ERROR_NON_EXISTENT_FILE_IN_PARAM);
    }

    // Load directory
    $content = scandir($dirName);

    $files = [];
    foreach ($content as $file) {
        // Skips invalid directories
        if ($file == "." || $file == "..") {
            continue;
        }

        // Recursively get files from subdirectories
        global $argRecursive;
        if ($argRecursive && is_dir($dirName.'/'.$file)) {
            $files2 = getFiles($dirName.'/'.$file);
            $files = array_merge($files, $files2);
        }

        // If extension is valid, the program adds file into list
        if (
            str_ends_with($file, ".src")
            || str_ends_with($file, ".rc")
            || str_ends_with($file, ".in")
            || str_ends_with($file, ".out")
        ) {
            $files[] = $dirName.'/'.$file;
        }
    }

    return $files;
}

/**
 * @brief Generates HTML sidebar with tests
 * @param array $tests List of the tests
 * @return void
 */
function generateSideBar(array $tests) {
    echo "<nav id='sidebar'>\n";

    // Generates title
    echo "<h1>Tests</h1>\n";

    echo "<ol>\n";

    foreach ($tests as $test) {
        // Skips test if there is no source file
        if (!$test->isValid()) {
            continue;
        }

        $id = $test->getId();
        echo "<li><a style='color: ";

        // Sets text color
        if ($test->getResult())
            echo "green";
        else
            echo "red";

        // Generates text with id
        echo "' href='#".$id."'>".$id."</a></li>";
    }

    echo "</ol>\n";

    echo "</nav>\n";
}

/**
 * @brief Generates HTML table with tests summarize
 * @param int $successfulTests Number of successful tests
 * @param int $errorTests Number of error tests
 * @return void
 */
function generateTable(int $successfulTests, int $errorTests) {
    echo "\t<table style=\"width:100%\" id='t01'>\n";

    echo "\t\t<thead>\n";
    echo "\t\t\t<caption><h1>Results of the test.php file</h1></caption>";
    echo "\t\t\t<tr>\n";
    echo "\t\t\t\t<th>Type of tests</td>\n";
    echo "\t\t\t\t<th>Count</td>\n";
    echo "\t\t\t</tr>\n";
    echo "\t\t</thead>\n";

    echo "\t\t<tbody>\n";
    echo "\t\t\t<tr>\n";
    echo "\t\t\t\t<td>Successful Tests</td>\n";
    echo "\t\t\t\t<td style='text-align: center'>".$successfulTests."</td>\n";
    echo "\t\t\t</tr>\n";
    echo "\t\t\t<tr>\n";
    echo "\t\t\t\t<td>Error Tests</td>\n";
    echo "\t\t\t\t<td style='text-align: center'>".$errorTests."</td>\n";
    echo "\t\t\t</tr>\n";
    echo "\t\t</tbody>\n";

    echo "\t</table>\n";

    echo "\t<hr/>";
}

// CLASSES

/**
 * Class test contains information about every test and functions for working with each test and generating HTML
 */
class Test {
    private string $path;
    private string $name;

    private string|bool $fileSrc = false;
    private string|bool $fileIn = false;
    private string|bool $fileOut = false;
    private string|bool $fileRc = false;

    private string|bool $yourOut = false;

    private int $returnCode = 0;
    private bool $outputsIdentical;

    /**
     * @brief Sets path and name of the test
     * @param string $pathName Path and name of the test
     */
    function __construct(string $pathName) {
        // Divides $pathName into two variables
        if ($lastBackslash = strrpos($pathName, '/')) {
            $path = substr($pathName, 0, $lastBackslash+1);
            $name = substr($pathName, $lastBackslash+1, strlen($pathName) - $lastBackslash);
        }
        else {
            $path = '';
            $name = $pathName;
        }

        $this->path = $path;
        $this->name = $name;
    }

    /**
     * @brief Sets file in test by extension
     * @param string $fileName File with extension
     * @return void
     */
    function setFile(string $fileName) {
        if (str_ends_with($fileName, ".src"))
            $this->fileSrc = $fileName;
        elseif (str_ends_with($fileName, ".in"))
            $this->fileIn = $fileName;
        elseif (str_ends_with($fileName, ".out"))
            $this->fileOut = $fileName;
        elseif (str_ends_with($fileName, ".rc"))
            $this->fileRc = $fileName;
        else
            printErrorMessage('Unknown file: '.$fileName, ERROR_INTERN);
    }

    /**
     * @return bool Test validity according to source file
     */
    function isValid(): bool {
        if ($this->fileSrc == false)
            return false;
        else
            return true;
    }

    /**
     * @return string Concatenation of the path and the string
     */
    function getId(): string {
        return $this->path.$this->name;
    }

    /**
     * @return bool Result if test is valid
     */
    function getResult(): bool {
        $expectedRc = intval(file_get_contents($this->fileRc));
        $result = $this->returnCode == $expectedRc;

        $outputsIdentical = $this->returnCode != 0 || $this->fileOut == false || $this->outputsIdentical;
        return $result && $outputsIdentical;
    }

    /**
     * @brief Generates missing files
     * @return void
     */
    function generateMissingFiles() {
        if ($this->fileSrc == false) {
            $this->fileSrc = $this->generateFile('.src', "");
        }

        if ($this->fileIn == false) {
            $this->fileIn = $this->generateFile(".in", "");
        }

        if ($this->fileRc == false) {
            $this->fileRc = $this->generateFile(".rc", "0");
        }
    }

    /**
     * @brief test for parser
     * @return void
     */
    function parserTest() {
        // Sets source file
        if ($this->fileSrc)
            $sourceParam = '<'.$this->fileSrc;
        else
            $sourceParam = '';

        // Generates file for output
        $this->yourOut = $this->generateFile(".xml", "");

        // Creates command for parser test
        global $argParserScript;
        $command = 'php8.1 '.$argParserScript.' '.$sourceParam.' >'.$this->yourOut.' 2>/dev/null';

        // Executes command
        exec($command, result_code: $this->returnCode);
    }

    /**
     * @brief test for interpreter
     * @return void
     */
    function interpretTest() {
        // If parser test failed, don't do interpreter test
        if ($this->returnCode != 0)
            return;

        // Sets source file for interpreter
        if ($this->yourOut == false)
            $sourceParam = '--source='.$this->fileSrc;
        else
            $sourceParam = '--source='.$this->yourOut;

        // Sets input file
        $inputParam = '--input='.$this->fileIn;

        // Generates temporary output file
        $outputFile = $this->generateFile(".your_out", "");
        $this->yourOut = $outputFile;

        // Creates command for interpreter test
        global $argIntScript;
        $command = 'python3.8 '.$argIntScript.' '.$sourceParam.' '.$inputParam.' >'.$outputFile.' 2>/dev/null';

        // Executes command
        exec($command, result_code: $this->returnCode);
    }

    /**
     * @brief Checks if output files are identical
     * @return void
     */
    function setOutputsIdentity() {
        // Checks if test could be valid
        if ($this->returnCode != 0 || !$this->fileOut) {
            return;
        }

        $rcDiff = 0;

        global $argParseOnly;
        global $argJexampath;
        if ($argParseOnly) {
            // If parse only argument is on, compare output files as xml-s
            $diffFile = $this->generateFile(".diff_xml", "");
            $command = "java -jar ".$argJexampath."jexamxml.jar ".
                $this->fileOut." ".$this->yourOut." ".$diffFile." /D ".$argJexampath."options 2>/dev/null";
        }
        else {
            // Compare output files with 'diff' command
            $diffFile = $this->generateFile(".diff_out", "");
            $command = "diff ".$this->fileOut." ".$this->yourOut." >".$diffFile." 2>/dev/null";
        }

        // Executes command
        exec($command, result_code: $rcDiff);

        // Decides if outputs are identical by output code
        if ($rcDiff == 0) {
            $this->outputsIdentical = true;
        }
        elseif ($rcDiff == 1) {
            $this->outputsIdentical = false;
        }
        else {
            printErrorMessage('Command for checking files identity failed', ERROR_NON_EXISTENT_FILE_IN_PARAM);
        }
    }

    /**
     * @brief Creates new file and add it to the list of files for delete
     * @param string $extension File extension
     * @param string $content Content of the new file
     * @return string
     */
    function generateFile(string $extension, string $content): string {
        // Creates new file name
        $fileName = $this->getId().$extension;

        // Creates new file
        file_put_contents($fileName, $content);

        // Adds filename to the list for deletes
        global $filesForDelete;
        $filesForDelete[] = $fileName;

        return $fileName;
    }

    /**
     * @brief Prints test into HTML
     * @return void
     */
    function printTest() {
        // HTML Title
        $this->generate_test_head();

        // HTML test result
        $this->generate_test_result();

        // HTML return codes comparison
        $this->generate_rc_text();

        // HTML outputs comparison
        $this->generateDiff();

        // HTML expand codes
        # region Expand codes
        if ($sourceCode = $this->fileSrc)
            $this->generate_expand_code("Source code", $sourceCode);

        if ($this->returnCode == 0) {
            if ($outputFile = $this->fileOut)
                $this->generate_expand_code("Expected output", $outputFile);

            if ($yourOutFile = $this->yourOut)
                $this->generate_expand_code("Test output", $yourOutFile);
        }
        # endregion

        // HTML <hr>
        $this->generate_hr();
    }

    // region Generating HTML

    /**
     * @brief Generates test title
     * @return void
     */
    function generate_test_head() {
        echo "<h2><a id='".$this->path.$this->name."'>".$this->path.$this->name."</a></h2>\n";
    }

    /**
     * @brief Generates test result
     * @return void
     */
    function generate_test_result() {
        echo "<p class='result'>\n";
        echo "\t<a>Test result: </a>\n";

        // Sets text color and prints result
        if ($this->getResult()) {
            echo "\t<a style='color: green'>\n";
            echo "\t\tSUCCESS\n";
        }
        else {
            echo "\t<a style='color: red'>\n";
            echo "\t\tFAIL\n";
        }

        echo "\t</a>\n";

        echo "</p>\n";
    }

    /**
     * @brief Generates return codes comparison
     * @return void
     */
    function generate_rc_text() {
        $rc = $this->returnCode;
        $expectedRc = intval(file_get_contents($this->fileRc));

        echo "\t<p class='return_code'>\n";

        // Sets text color
        if ($rc == $expectedRc) {
            echo "\t\t<a style='color: green'>\n";
        }
        else {
            echo "\t\t<a style='color: red'>\n";
        }

        // Prints text
        echo "\t\t\t"."Return code of the test: ".$rc."<br>\n";
        echo "\t\t\t"."Expected return code: ".$expectedRc."<br>\n";
        echo "\t\t</a>\n";

        echo "\t</p>\n";
    }

    /**
     * @brief Generates expand code
     * @param string $name Name of expand code element
     * @param string $file File with code
     * @return void
     */
    function generate_expand_code(string $name,string $file)
    {
        echo "\t<section>\n";
        echo "\t\t<details>\n";

        // Prints title for the code
        echo "\t\t\t<summary>\n";
        echo "\t\t\t\t<span>".$name."</span>\n";
        echo "\t\t\t</summary>\n";

        echo "\t\t\t<pre><code class='code'>\n";

        // Printing code lines
        $lineNum = 1;
        $handle = fopen($file, "r");
        if ($handle) {
            while (($line = fgets($handle)) != false) {
                $line = str_replace('<', "<a><</a>", $line);
                echo "\t\t\t\t<div style='background-color: lightgray; padding: 5px'>$lineNum\t$line</div>\n";
                $lineNum += 1;
            }
        }

        fclose($handle);

        echo "\t\t\t</code></pre>\n";

        echo "\t\t</details>\n";
        echo "\t</section>\n";
    }

    /**
     * @brief Generates output difference or identical outputs message
     * @return void
     */
    function generateDiff() {
        // Skips if there are no files for comparison
        if ($this->returnCode != 0 || !$this->fileOut) {
            return;
        }

        echo "\t<p class='test_diff'>\n";

        // Prints comparison result
        if ($this->outputsIdentical) {
            echo "\t\t<a style='color: green'>\n";
            echo "\t\t\tOutput files are identical\n<br>\n";
        }
        else {
            echo "\t\t<a style='color: red'>\n";
            echo "\t\t\tOutput files are different\n<br>\n";
        }

        echo "\t\t</a>\n";

        echo "\t</p>\n";
    }

    /**
     * @brief Generates hr
     * @return void
     */
    function generate_hr() {
        echo "\t<hr/>\n";
    }

    // endregion
}

// GLOBAL VARIABLES
$filesForDelete = [];

// PROGRAM ARGUMENTS
$argDirWithTests = ".";
$argRecursive = false;
$argParserScript = "parse.php";
$argIntScript = "interpret.py";
$argParseOnly = false;
$argIntOnly = false;
$argJexampath = "/pub/courses/ipp/jexamxml/";
$argNoClean = false;

// ARGUMENTS LOADING
$isFirst = true;
foreach ($argv as $arg) {
    // Skips first argument, because it's the 'test.php'
    if ($isFirst) {
        $isFirst = false;
        continue;
    }

    // Sets global argument variables
    if ($arg == "--help") {
        // Help message
        if ($argc != 2) {
            printErrorMessage("Invalid combination of the parameters", ERROR_PARAMETERS);
        }

        printHelpMessage();
    }
    elseif (str_starts_with($arg, "--directory=")) {
        // Sets a path to directory with tests
        $argDirWithTests = substr($arg, strlen("--directory="));

        if (str_ends_with($argDirWithTests, '/')) {
            $argDirWithTests = substr($argDirWithTests, 0, -1);
        }
    }
    elseif ($arg == "--recursive") {
        // Directory with tests will be searched recursively in subdirectories
        $argRecursive = true;
    }
    elseif (str_starts_with($arg, "--parse-script=")) {
        // Sets parse script
        $argParserScript = substr($arg, strlen("--parse-script="));
        if (!file_exists($argParserScript))
            printErrorMessage("Non existent file for parser", ERROR_NON_EXISTENT_FILE_IN_PARAM);
    }
    elseif (str_starts_with($arg, "--int-script=")) {
        // Sets interpreter scripts
        $argIntScript = substr($arg, strlen("--int-script="));
        if (!file_exists($argIntScript))
            printErrorMessage("Non existent file for interpreter", ERROR_NON_EXISTENT_FILE_IN_PARAM);
    }
    elseif ($arg == "--parse-only") {
        // The program runs only tests for parser
        if (in_array("--int-only", $argv) || preStringInArray("--int-script=", $argv)) {
            printErrorMessage("Invalid combination of the parameter: ".$arg, ERROR_PARAMETERS);
        }
        $argParseOnly = true;
    }
    elseif ($arg == "--int-only") {
        // The program runs only tests for interpreter
        if (
                in_array("--parse-only", $argv)
                || preStringInArray("--parse-script=", $argv)
                || preStringInArray("--jexampath=", $argv)
        ) {
            printErrorMessage("Invalid combination of the parameter: ".$arg, ERROR_PARAMETERS);
        }

        $argIntOnly = true;
    }
    elseif (str_starts_with($arg, "--jexampath=")) {
        // Path into directory with jexamxml file and options
        $argJexampath = substr($arg, strlen("--jexampath="));

        if (!str_ends_with($argJexampath, '/'))
            $argJexampath .= '/';
    }
    elseif ($arg == "--noclean") {
        // Temporary files won't be deleted
        $argNoClean = true;
    }
    else {
        printErrorMessage("Unknown parameter: ".$arg, ERROR_PARAMETERS);
    }
}

?>
<!DOCTYPE html>
<html lang="en-us" style="background-color: antiquewhite">
<head>
    <meta charset="UTF-8">
    <title>Output of the test.php file</title>
    <style>
        h1 {
            text-align: center;
        }
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 15px;
        }
        table#t01 tr:nth-child(even) {
            background-color: #e2817b;
        }
        table#t01 tr:nth-child(odd) {
            background-color: #90e27b;
        }
        table#t01 th {
            color: white;
            background-color: black;
        }
        pre {
            width: 100%;
            margin-left: 40px;
        }
        code {
            width: 100%;
            font-family: monospace;
        }
        details {
            width: 100%;
            background-color: #e2e2e2;
            padding: 10px;
        }
        a {
            font-family: sans-serif;
        }
        li {
            padding: 10px;
        }
        #sidebar {
            height: 100%;
            width: 300px;
            position: fixed;
            z-index: 1;
            top: 0;
            left: 0;
            background-color: coral;
            overflow-x: hidden;
            padding-top: 20px;
        }
        .main {
            margin-left: 300px;
            padding: 10px;
        }
    </style>
</head>
<body class="main">
<?php

/**
 * Gets the files for tests
 */
$files = getFiles($argDirWithTests);

$tests = [];

/**
 * Transferring files into tests
 */
foreach ($files as $file) {
    // Gets filename without extension
    $fileName = substr($file, 0, strrpos($file, '.'));

    // Checks if file is in the list, then creates new one or set it
    if (!array_key_exists($fileName, $tests))
        $test = new Test($fileName);
    else
        $test = $tests[$fileName];

    $test->setFile($file);
    $tests[$fileName] = $test;
}

// Sorts array by key
ksort($tests);

$successfulTests = 0;
$errorTests = 0;
/**
 * Works with tests
 */
foreach ($tests as $test) {
    // Skips test if there is no source file
    if (!$test->isValid()) {
        continue;
    }

    // Generate missing files .out, .in and .src
    $test->generateMissingFiles();

    // Makes the tests for parse and interpret
    if ($argParseOnly) {
        $test->parserTest();
    }
    elseif ($argIntOnly) {
        $test->interpretTest();
    }
    else {
        $test->parserTest();
        $test->interpretTest();
    }

    // Sets if output files are identical
    $test->setOutputsIdentity();

    // Counts successful and error number of tests
    if ($test->getResult()) {
        $successfulTests += 1;
    }
    else {
        $errorTests += 1;
    }
}

/**
 * Generates HTML sidebar
 */
generateSideBar($tests);

/**
 * Generates tests summarize
 */
generateTable($successfulTests, $errorTests);

/**
 * Prints the tests in HTML
 */
foreach ($tests as $test) {
    // Skips test if there is no source file
    if (!$test->isValid()) {
        continue;
    }

    $test->printTest();
}

/**
 * Cleans directory with temporary files
 */
if (!$argNoClean) {
    foreach ($filesForDelete as $file) {
        shell_exec('rm '.$file);
    }
}

?>
</body>
</html>
