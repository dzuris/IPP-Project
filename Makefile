CC=php8.1
FILES=test.php
HELP_MESSAGE_PARAMS=--help

help_message:
	$(CC) $(FILES) $(HELP_MESSAGE_PARAMS)
