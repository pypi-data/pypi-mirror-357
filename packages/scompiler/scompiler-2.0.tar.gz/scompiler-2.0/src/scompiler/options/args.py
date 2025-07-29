# See LICENSE file for copyright and license details.
"""Module to get args from command."""
import argparse
from dataclasses import fields

from scompiler.options import config
from scompiler.options.options import Options, OptionsActions, OptionsMode


LIST_ARGS = {
	"file_type": {
		"--latex": "Use texlive",
		"--mbed": "Use mbed-tools",
		"--python": "Use python",
	},
	"actions": {
		"--save":
		{
			"short": "-s",
			"help": "Save in current directory, by default is save in /tmp",
			"action": "store_true",
		},
		"--version": {
			"short": "-v",
			"help": "Print the version",
			"action": "store_true",
		},
		"--clear": {
			"short": "-c",
			"help": "Clear all tmp directory",
			"action": "store_true",
		},
	},
	"options": {
		"latex":
		{
			"--biber":
			{
				"short": "-b",
				"help": "Use biber",
				"action": "store_true",
			},
		},
		"mbed":
		{
			"--nucleo":
			{
				"short": "-n",
				"help": "Define the nucleo of STM",
				"type": str,
				"metavar": "nucleo",
			},
		},
		"python":
		{
			"--package":
			{
				"short": "-p",
				"help": "Run as package. Without, run as script",
				"action": "store_true",
			},
		},
	},
}


def get_args():
	"""Get arguments."""

	message_usage = (
		"\n"
		"  %(prog)s [actions]\n"
		"  %(prog)s [type code] [options] [file]\n"
	)

	# Create arguments
	parser = argparse.ArgumentParser(usage=message_usage)
	parser.add_argument("file", nargs='?', default='')

	# Add type
	type_code = parser.add_argument_group("type code")
	for opt, arg in LIST_ARGS["file_type"].items():
		type_code.add_argument(opt, help=arg, action="store_true")

	# Add global option
	global_options = parser.add_argument_group("global options")
	for opt, arg in LIST_ARGS["actions"].items():
		opt = [opt, arg.pop("short", None)]
		global_options.add_argument(*opt, **arg)

	# Add options
	for file_type, arg in LIST_ARGS["options"].items():
		type_options = parser.add_argument_group(file_type)
		for command, command_args in arg.items():
			command = [command, command_args.pop("short", None)]
			type_options.add_argument(*command, **command_args)

	return vars(parser.parse_args())


def set_config(args):
	"""Get the current option."""

	# Set general options
	options_elements = {field.name for field in fields(Options)}
	args_options = {
		k: v for k, v in args.items() if k in options_elements
	}
	config.options = Options(
		**{
			key: args_options.get(key, False)
			for key in Options.__annotations__
		}
	)

	# Set actions options
	options_elements = {field.name for field in fields(OptionsActions)}
	args_options = {
		k: v for k, v in args.items() if k in options_elements
	}
	config.options.actions = OptionsActions(
		**{
			key: args_options.get(key, False)
			for key in OptionsActions.__annotations__
		}
	)

	# Set options
	options_elements = {field.name for field in fields(OptionsMode)}
	args_options = {
		k: v for k, v in args.items() if k in options_elements
	}
	config.options.options = OptionsMode(
		**{
			key: args_options.get(key, False)
			for key in OptionsMode.__annotations__
		}
	)

	# Set file type
	file_type = []
	for key, _ in LIST_ARGS["file_type"].items():
		if args[key[2:]]:
			file_type.append(key[2:])

	if len(file_type) == 1:
		file_type = file_type[0]
	else:
		file_type = None
	config.options.file_type = file_type


__all__ = ['get_args', 'set_config']
