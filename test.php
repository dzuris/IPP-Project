<!--
    @project Testing program
    @file test.php
    @email xdzuri00@stud.fit.vutbr.cz
    @author Adam Dzurilla
-->

<!-- GLOBAL VARIABLES -->
<?php
    $param_parser = null;
    $param_interpret = null;
    $testDir = null;
    $recursive = false;
?>

<!-- FUNCTIONS -->
<?php

function generate_error_test_head($testName)
{
    echo "<p_red>";
    echo "\t" . $testName;
    echo "</p_red>";
}

function generate_expand_code($name, $file)
{
    echo "<section>";
    echo "\t<details class=\"source\">";

    echo "\t\t<summary>";
    echo "\t\t\t<span>".$name."</span>";
    echo "\t\t</summary>";

    echo "\t\t<pre>";
    echo "\t\t\t<code>";

    echo file_get_contents($file);

    echo "\t\t\t</code>";
    echo "\t\t</pre>";

    echo "\t</detials>";
    echo "</section>";
}

function generate_hr() {
    echo "<hr/>";
}

?>

<!DOCTYPE html>
<html lang="html5">
<head>
    <meta charset="UTF-8">
    <title>Test output file</title>
    <style>
        p_red {
            color: red;
        }

        p_green {
            color: green;
        }
    </style>
</head>
<body>
<h1 style="text-align:center;">
    Results of the parse.php file
</h1>
<hr/>
<?php

generate_error_test_head("Hello");
generate_expand_code("Expand", "inputf.txt");
generate_hr();

?>
</body>
</html>
