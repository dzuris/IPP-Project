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
function print_error_message(string $message,int $error_code): void {
    error_log($message);
    exit($error_code);
}

/**
 * @brief Prints help message for the program
 * @return void
 */
function print_help_message(): void {
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

function getFiles(string $dirName): array {
    global $arg_recursive;

    if (!file_exists($dirName)) {
        print_error_message("Fail in opening directory with tests", ERROR_NON_EXISTENT_FILE_IN_PARAM);
    }

    $content = scandir($dirName);

    $files = [];
    foreach ($content as $file) {
        if ($file == "." || $file == "..") {
            continue;
        }

        if ($arg_recursive && is_dir($dirName.'/'.$file)) {
            $files2 = getFiles($dirName.'/'.$file);
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

function generateSideBar(array $tests) {
    echo "<nav id='sidebar'>\n";

    echo "<h1>Tests</h1>\n";

    echo "<ol>\n";

    foreach ($tests as $test) {
        $id = $test->getId();
        echo "<li><a style='color: ";

        if ($test->getResult())
            echo "green";
        else
            echo "red";

        echo "' href='#".$id."'>".$id."</a></li>";
    }

    echo "</ol>\n";

    echo "</nav>\n";
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
    private bool $outputsIdentical;

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

    function getId(): string {
        return $this->path.$this->name;
    }

    function getResult(): bool {
        $expectedRc = intval(file_get_contents($this->fileRc));
        $result = $this->returnCode == $expectedRc;
        $outputsIdentical = $this->returnCode != 0 || $this->fileOut == false || $this->outputsIdentical;
        return $result && $outputsIdentical;
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
        $command = 'php8.1 '.$arg_parserScript.' '.$sourceParam.' >'.$this->yourOut.' 2>/dev/null';

        exec($command, result_code: $this->returnCode);
    }

    function interpretTest() {
        if ($this->returnCode != 0)
            return;

        if ($this->yourOut == false)
            $sourceParam = '--source='.$this->fileSrc;
        else
            $sourceParam = '--source='.$this->yourOut;

        $inputParam = '--input='.$this->fileIn;

        $outputFile = $this->generateFile("_your.out", "");
        $this->yourOut = $outputFile;

        global $arg_intScript;
        $command = 'python3.8 '.$arg_intScript.' '.$sourceParam.' '.$inputParam.' >'.$outputFile.' 2>/dev/null';

        exec($command, result_code: $this->returnCode);
    }

    function setOutputsIdentical() {
        if ($this->returnCode != 0 || !$this->fileOut) {
            return;
        }

        $rcDiff = 0;

        global $arg_parseOnly;
        global $arg_jexampath;
        if ($arg_parseOnly) {
            $diffFile = $this->generateFile("_diff.xml", "");
            $command = "java -jar ".$arg_jexampath."jexamxml.jar ".
                $this->fileOut." ".$this->yourOut." ".$diffFile." /D ".$arg_jexampath."options 2>/dev/null";
        }
        else {
            $diffFile = $this->generateFile("_diff.out", "");
            $command = "diff ".$this->fileOut." ".$this->yourOut." >".$diffFile." 2>/dev/null";
        }

        exec($command, result_code: $rcDiff);

        if ($rcDiff == 0) {
            $this->outputsIdentical = true;
        }
        elseif ($rcDiff == 1) {
            $this->outputsIdentical = false;
        }
        else {
            print_error_message('Command for checking files identity failed', ERROR_NON_EXISTENT_FILE_IN_PARAM);
        }
    }

    function generateFile($extension, $content): string {
        $fileName = $this->path.$this->name.$extension;

        file_put_contents($fileName, $content);

        global $filesForDelete;
        $filesForDelete[] = $fileName;

        return $fileName;
    }

    function printTest() {
        $this->generate_test_head();

        $this->generate_test_result();

        $this->generate_rc_text();

        $this->generateDiff();

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

        $this->generate_hr();
    }

    // region Generating HTML
    function generate_test_head() {
        echo "<h2><a id='".$this->path.$this->name."'>".$this->path.$this->name."</a></h2>\n";
    }

    function generate_test_result() {
        echo "<p class='result'>\n";
        echo "\t<a>Test result: </a>\n";

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

    function generate_rc_text() {
        $rc = $this->returnCode;
        $expectedRc = intval(file_get_contents($this->fileRc));

        echo "\t<p class='return_code'>\n";

        if ($rc == $expectedRc) {
            echo "\t\t<a style='color: green'>\n";
        }
        else {
            echo "\t\t<a style='color: red'>\n";
        }

        echo "\t\t\t"."Return code of the test: ".$rc."\n<br>\n";
        echo "\t\t\t"."Expected return code: ".$expectedRc."\n<br>\n";
        echo "\t\t</a>\n";

        echo "\t</p>\n";
    }

    function generate_expand_code(string $name,string $file)
    {
        echo "\t<section>\n";
        echo "\t\t<details>\n";

        echo "\t\t\t<summary>\n";
        echo "\t\t\t\t<span>".$name."</span>\n";
        echo "\t\t\t</summary>\n";

        echo "\t\t\t<pre><code class='code'>\n";

        $lineNum = 1;
        $handle = fopen($file, "r");
        if ($handle) {
            while (($line = fgets($handle)) != false) {
                $line = str_replace('<', "<a><</a>", $line);
                echo "<div style='background-color: lightgray; padding: 5px'>$lineNum\t$line</div>\n";
                $lineNum += 1;
            }
        }

        fclose($handle);

        echo "\t\t\t</code></pre>\n";

        echo "\t\t</details>\n";
        echo "\t</section>\n";
    }

    function generateDiff() {
        if ($this->returnCode != 0 || !$this->fileOut) {
            return;
        }

        echo "\t<p class='test_diff'>\n";

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

    function generate_hr() {
        echo "\t<hr/>\n";
    }

    // endregion
}

// GLOBAL VARIABLES
$filesForDelete = [];

// PROGRAM ARGUMENTS
$arg_testDir = ".";
$arg_recursive = false;
$arg_parserScript = "parse.php";
$arg_intScript = "interpret.py";
$arg_parseOnly = false;
$arg_intOnly = false;
$arg_jexampath = "/pub/courses/ipp/jexamxml/";
$arg_noClean = false;

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
        if (str_ends_with($arg_testDir, '/')) {
            $arg_testDir = substr($arg_testDir, 0, -1);
        }
    }
    elseif ($arg == "--recursive") {
        $arg_recursive = true;
    }
    elseif (str_starts_with($arg, "--parse-script=")) {
        $arg_parserScript = substr($arg, strlen("--parse-script="));
        if (!file_exists($arg_parserScript))
            print_error_message("Non existent file for parser", ERROR_NON_EXISTENT_FILE_IN_PARAM);
    }
    elseif (str_starts_with($arg, "--int-script=")) {
        $arg_intScript = substr($arg, strlen("--int-script="));
        if (!file_exists($arg_intScript))
            print_error_message("Non existent file for interpreter", ERROR_NON_EXISTENT_FILE_IN_PARAM);
    }
    elseif ($arg == "--parse-only") {
        if (in_array("--int-only", $argv) || pre_string_in_array("--int-script=", $argv)) {
            print_error_message("Invalid combination of the parameter: ".$arg, ERROR_PARAMETERS);
        }
        $arg_parseOnly = true;
    }
    elseif ($arg == "--int-only") {
        if (
                in_array("--parse-only", $argv)
                || pre_string_in_array("--parse-script=", $argv)
                || pre_string_in_array("--jexampath=", $argv)
        ) {
            print_error_message("Invalid combination of the parameter: ".$arg, ERROR_PARAMETERS);
        }

        $arg_intOnly = true;
    }
    elseif (str_starts_with($arg, "--jexampath=")) {
        $arg_jexampath = substr($arg, strlen("--jexampath="));

        if (!str_ends_with($arg_jexampath, '/'))
            $arg_jexampath .= '/';
    }
    elseif ($arg == "--noclean") {
        $arg_noClean = true;
    }
    else {
        print_error_message("Unknown parameter: ".$arg, ERROR_PARAMETERS);
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
<h1>
    Results of the test.php file
</h1>
<hr/>
<?php

$files = getFiles($arg_testDir);

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

    $test->setOutputsIdentical();
}

generateSideBar($tests);

foreach ($tests as $test) {
    $test->printTest();
}

/**
 * Cleans directory with temporary files
 */
if (!$arg_noClean) {
    foreach ($filesForDelete as $file) {
        shell_exec('rm '.$file);
    }
}

?>
</body>
</html>
