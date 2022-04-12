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
    <p_red>
        <?php
            echo "ahoj\n";
        ?>
    </p_red>
    <section id="section-intro">
        <details class="source">
            <summary>
                <span>Expand source code</span>
            </summary>
            <pre>
                <code class="python">
                    <?php
                        $fh = fopen("tests/xmls/test1.xml", "r");
                        $data = fread($fh, 10000);
                        fclose($fh);
                        echo $data;
                    ?>
                </code>
            </pre>
        </details>
    </section>
</body>
</html>