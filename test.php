<?php
/**
 * @project Testing program
 * @file test.php
 * @email xdzuri00@stud.fit.vutbr.cz
 * @author Adam Dzurilla
 */

// ERROR CODES
const NO_ERROR = 0;
const ERROR_PARAMETERS = 10; // missing parameter or forbidden combination of the parameters
const ERROR_OPEN_INPUT_FILE = 11;
const ERROR_OPEN_OUTPUT_FILE = 12;
const ERROR_NON_EXISTENT_FILE_IN_PARAM = 41;    // directory, parser, interpreter, jexamxml
const ERROR_INTERN = 99; // Internal error

// GLOBAL CONSTANTS
const TESTS_DIRECTORY = 'directoryTestsXdzuri00/';

// GLOBAL FUNCTIONS
/**
 * @param string $message Brief error message
 * @param int $error_code Error return code
 * @return void
 */
function print_error_message(string $message,int $error_code) {
    error_log($message);
    exit($error_code);
}

/**
 * @brief Prints help message for the program
 * @return void
 */
function print_help_message() {
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
 * @param string $preString expected start of the string
 * @param array $array string values
 * @return bool if some string from the array starts with pre string
 */
function pre_string_in_array(string $preString, array $array): bool
{
    foreach ($array as $i) {
        if (str_starts_with($i, $preString)) {
            return true;
        }
    }

    return false;
}

// PROGRAM ARGUMENTS
$arg_testDir = ".";
$arg_recursive = false;
$arg_parserScript = "parse.php";
$arg_intScript = "interpret.py";
$arg_parseOnly = false;
$arg_intOnly = false;
$arg_jexampath = "/pub/courses/ipp/jexamxml/";
$arg_noClean = false;

// GLOBAL VARIABLES
$order = 1;
$filesForDelete = [];

// ARGUMENTS LOADING
$isFirst = true;
foreach ($argv as $arg) {
    if ($isFirst) {
        $isFirst = false;
        continue;
    }

    if ($arg == "--help") {
        if ($argc != 2) {
            print_error_message("Invalid combination of the parameters", ERROR_PARAMETERS);
        }
        print_help_message();
    }
    elseif (str_starts_with($arg, "--directory=")) {
        $arg_testDir = substr($arg, strlen("--directory="));
    }
    elseif ($arg == "--recursive") {
        $arg_recursive = true;
    }
    elseif (str_starts_with($arg, "--parse-script=")) {
        $arg_parserScript = substr($arg, strlen("--parse-script="));
    }
    elseif (str_starts_with($arg, "--int-script=")) {
        $arg_intScript = substr($arg, strlen("--int-script="));
    }
    elseif ($arg == "--parse-only") {
        if (in_array("--int-only", $argv) || pre_string_in_array("--int-script=", $argv)) {
            print_error_message("Invalid combination of the parameter: --parse-only", ERROR_PARAMETERS);
        }
        $arg_parseOnly = true;
    }
    elseif ($arg == "--int-only") {
        if (
                in_array("--parse-only", $argv)
                || pre_string_in_array("--parse-script=", $argv)
                || pre_string_in_array("--jexampath=", $argv)
        ) {
            print_error_message("Invalid combination of the parameter: --int-only", ERROR_PARAMETERS);
        }

        $arg_intOnly = true;
    }
    elseif (str_starts_with($arg, "--jexampath=")) {
        $arg_jexampath = substr($arg, strlen("--jexampath="));
    }
    elseif ($arg == "--noclean") {
        $arg_noClean = true;
    }
    else {
        print_error_message("Unknown parameter: ".$arg, ERROR_PARAMETERS);
    }
}

// CLASSES
class Test {
    private string $path;
    private string $name;

    private string|bool $fileSrc = false;
    private string|bool $fileIn = false;
    private string|bool $fileOut = false;
    private string|bool $fileRc = false;

    private string|bool $yourOut = false;

    private int $returnCode = 0;
    private bool $result = false;

    function __construct($pathName) {
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

    function setFile($fileName) {
        if (str_ends_with($fileName, ".src"))
            $this->fileSrc = $fileName;
        elseif (str_ends_with($fileName, ".in"))
            $this->fileIn = $fileName;
        elseif (str_ends_with($fileName, ".out"))
            $this->fileOut = $fileName;
        elseif (str_ends_with($fileName, ".rc"))
            $this->fileRc = $fileName;
        else
            print_error_message('Unknown file: '.$fileName, ERROR_INTERN);
    }

    function generateMissingFiles() {
        if ($this->fileIn == false) {
            $this->fileIn = $this->generateFile(".in", "");
        }

        if ($this->fileRc == false) {
            $this->fileRc = $this->generateFile(".rc", "0");
        }
    }

    function parserTest() {
        if ($this->fileSrc)
            $sourceParam = '<'.$this->fileSrc;
        else
            $sourceParam = '';

        $this->yourOut = $this->generateFile(".xml", "");

        global $arg_parserScript;
        $command = 'php8.1 '.$arg_parserScript.' '.$sourceParam.'>'.$this->yourOut;
        shell_exec($command);

        $this->returnCode = intval(shell_exec('echo $?'));
    }

    function interpretTest() {
        if ($this->returnCode != 0)
            return;

        if ($this->yourOut == false)
            $sourceParam = '--source='.$this->fileSrc;
        else
            $sourceParam = '--source='.$this->yourOut;

        $inputParam = '--input='.$this->fileIn;

        $outputFile = $this->generateFile(".out2", "");
        $this->yourOut = $outputFile;

        global $arg_intScript;
        $command = 'python3.8 '.$arg_intScript.' '.$sourceParam.' '.$inputParam.' >'.$outputFile;
        shell_exec($command);
        //$rc = shell_exec('echo $?');
        echo $command."<br>\n";
        //echo $rc."<br>\n";

        //$this->returnCode = shell_exec('echo $?');
        $this->returnCode = intval(shell_exec('echo $?'));
    }

    function generateFile($extension, $content): string {
        $fileName = $this->path.$this->name.$extension;

        file_put_contents($fileName, $content);

        global $filesForDelete;
        $filesForDelete[] = $fileName;

        return $fileName;
    }

    function printTest() {
        generate_test_head($this->path.$this->name);

        echo "Src: ".$this->fileSrc."<br>\n";
        echo "In: ".$this->fileIn."<br>\n";
        echo "Out: ".$this->fileOut."<br>\n";
        echo "Rc: ".$this->fileRc."<br>\n";

        if ($this->fileRc)
            $expectedRc = intval(file_get_contents($this->fileRc));
        else
            $expectedRc = 0;

        generate_test_result($this->returnCode == $expectedRc);

        if ($this->fileRc)
            generate_rc_text($this->returnCode, $expectedRc);
        else
            generate_rc_text($this->returnCode, -1);

        if ($sourceCode = $this->fileSrc)
            generate_expand_code("Source code", $sourceCode);

        if ($outputFile = $this->fileOut)
            generate_expand_code("Expected output", $outputFile);

        generate_hr();
    }
}

// FUNCTIONS
function generate_test_head(string $testName) {
    echo "<h2>\n";
    echo "\t".$testName."\n";
    echo "</h2>\n";
}

function generate_test_result(bool $result) {
    echo "<p class='result'>\n";
    echo "\t<a>Test result: </a>\n";

    if ($result) {
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

function generate_text(string $text, string $tabulators="") {
    echo $tabulators."\t<a>\n";
    echo $tabulators."\t\t" . $text."\n";
    echo $tabulators."\t</a>\n";
}

function generate_red_text(string $text, string $tabulators="")
{
    echo $tabulators."\t<a style='color: red'>\n";
    echo $tabulators."\t\t" . $text."\n";
    echo $tabulators."\t<br>\n";
    echo $tabulators."\t</a>\n";
}

function generate_green_text(string $text, string $tabulators="")
{
    echo $tabulators."\t<a style='color: green'>\n";
    echo $tabulators."\t\t" . $text."\n";
    echo $tabulators."\t<br>\n";
    echo $tabulators."\t</a>\n";
}

function generate_expand_code(string $name,string $file)
{
    echo "\t<section>\n";
    echo "\t\t<details class=\"source\">\n";

    echo "\t\t\t<summary>\n";
    echo "\t\t\t\t<span>".$name."</span>\n";
    echo "\t\t\t</summary>\n";

    echo "\t\t\t<pre>\n";

    $data = file_get_contents($file);
    $data = str_replace("<", "<a><</a>", $data);

    echo $data."\n";
    echo "\t\t\t</pre>\n";

    echo "\t\t</details>\n";
    echo "\t</section>\n";
}

function generate_rc_text(int $rc,int $expectedRc) {
    echo "\t<p class='return_code'>\n";

    if ($rc == $expectedRc) {
        generate_green_text("Return code of the test: ".$rc, "\t");
        generate_green_text("Expected return code: ".$expectedRc, "\t");
    }
    elseif ($expectedRc == -1) {
        generate_green_text("Return code of the test: ".$rc, "\t");
        generate_text("Expected return code: NONE\n", "\t");
    }
    else {
        generate_red_text("Return code of the test: ".$rc, "\t");
        generate_red_text("Expected return code: ".$expectedRc, "\t");
    }

    echo "\t</p>\n";
}

function generate_hr() {
    echo "\t<hr/>\n";
}

function get_files(string $dirName): array {
    global $arg_recursive;
    $content = scandir($dirName);

    if ($content == false) {
        print_error_message("Fail in opening directory with tests", ERROR_NON_EXISTENT_FILE_IN_PARAM);
    }

    $files = [];
    foreach ($content as $file) {
        if ($file == "." || $file == "..") {
            continue;
        }

        if ($arg_recursive && is_dir($dirName.'/'.$file)) {
            $files2 = get_files($dirName.'/'.$file);
            $files = array_merge($files, $files2);
        }

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

function cleanDirectory() {
    shell_exec('rm -r '.TESTS_DIRECTORY);
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Output of the test.php file</title>
</head>
<body>
<h1 style="text-align:center;">
    Results of the test.php file
</h1>
<hr/>
<?php

$files = get_files($arg_testDir);

$tests = [];

/**
 * Transferring files into tests
 */
foreach ($files as $file) {
    $fileName = substr($file, 0, strrpos($file, '.'));

    if (!array_key_exists($fileName, $tests))
        $test = new Test($fileName);
    else
        $test = $tests[$fileName];

    $test->setFile($file);
    $tests[$fileName] = $test;
}

/**
 * Creates directory with temporary files
 */
//if (!file_exists(TESTS_DIRECTORY))
    //shell_exec('mkdir '.TESTS_DIRECTORY);

/**
 * Works with tests
 */
foreach ($tests as $test) {
    $test->generateMissingFiles();

    if ($arg_parseOnly) {
        $test->parserTest();
    }
    elseif ($arg_intOnly) {
        $test->interpretTest();
    }
    else {
        $test->parserTest();
        $test->interpretTest();
    }

    $test->printTest();
}

//$output = shell_exec('cat Makefile');
//echo $output;

/**
 * Cleans directory with temporary files
 */
if (!$arg_noClean) {
    //cleanDirectory();
    foreach ($filesForDelete as $file) {
        shell_exec('rm '.$file);
    }
}

?>
</body>
</html>
