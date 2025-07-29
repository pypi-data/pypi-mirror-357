# See LICENSE file for copyright and license details.
"""Import the package functions modules."""
import sys

from importlib.metadata import version

from scompiler.options import config
from scompiler.filetype.filetype import compiler
from scompiler.options.args import get_args, set_config
from scompiler.utils import clear_tmpdir


def scompiler_main():
	"""Main function to compile programs."""

	# Get args
	set_config(get_args())

	if config.options.actions.version:
		current_version = version("scompiler")
		print(f"scompiler-v{current_version}")
		return 0
	if config.options.actions.clear:
		clear_tmpdir()
		return 0

	return compiler()


def main():
	"""Entry point."""

	retval = scompiler_main()
	sys.exit(retval)


if __name__ == "__main__":
	main()
