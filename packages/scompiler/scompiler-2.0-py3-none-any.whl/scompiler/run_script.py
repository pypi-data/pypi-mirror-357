# See LICENSE file for copyright and license details.
"""Module to run script."""
import os
from pathlib import Path

from scompiler.message import message
from scompiler.options import config
from scompiler.utils import create_tmpdir, run_command


class RunScript():
	"""Runs Script Class."""

	command = ""
	extension = ""

	# File
	file = ""
	file_name = ""
	# Directory
	tmp_dir = ""
	current_dir = ""
	current_dir_name = ""

	def __init__(self, command, extension):
		"""Init function."""

		self.command = command
		self.extension = extension

	def run_script(self):
		"""Run script."""

		message.step("Prepare")

		if self.check_file():
			return -1

		# Copy to tmp directory
		self.current_dir = os.getcwd()
		self.current_dir_name = os.path.basename(self.current_dir)
		self.tmp_dir = create_tmpdir(self.current_dir_name)

		# Copy to tmp directory
		command = f"cp -r {config.options.file} {self.tmp_dir}/"
		status, _ = run_command(command.split())
		if status:
			message.error("Don't copy to tmp directory")
			return -2

		# Go to directory
		os.chdir(self.tmp_dir)
		config.options.file = os.path.basename(config.options.file)

		# Run
		message.step("Run")
		command = f"{self.command} {config.options.file}"
		status, _ = run_command(command, shell=True, capture=False)

		if status:
			message.error("Run script")
			return -3
		message.message("Success!!!")

		return 0

	def check_file(self):
		"""Check script file."""

		message.message("Check file")

		# Search file
		if not Path(config.options.file).is_file():
			message.error("Don't found any file")
			return -1

		# Check extension
		file = os.path.splitext(config.options.file)
		if file[1] != self.extension:
			message.error(f"Extension: {file[1]}")
			return -3

		return 0
