# See LICENSE file for copyright and license details.
"""Module entry point."""
from scompiler.options import config
from scompiler.message import message
from scompiler.filetype.latex import TypeLatex
from scompiler.filetype.python import TypePython
from scompiler.filetype.mbed import TypeMbed


def compiler():
	"""Select compiler by file type."""

	match config.options.file_type:
		case "latex":
			latex = TypeLatex()
			return latex.compiler()
		case "mbed":
			mbed = TypeMbed()
			return mbed.compiler()
		case "python":
			python = TypePython()
			return python.compiler()
		case _:
			message.error("Need only one file type")
			return -1

	return 0
