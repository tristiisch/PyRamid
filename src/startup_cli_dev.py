import debugpy
from pyramid.cli.startup import startup_cli

def startup_cli_dev():
	debugpy.listen(('0.0.0.0', 5679))
	debugpy.wait_for_client()
	startup_cli()

if __name__ == "__main__":
	startup_cli_dev()
