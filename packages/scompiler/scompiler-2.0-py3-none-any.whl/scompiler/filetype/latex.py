# See LICENSE file for copyright and license details.
"""LaTeX submodule."""
import os
from pathlib import Path

from scompiler.message import message
from scompiler.options import config
from scompiler import utils


class TypeLatex():
	"""Main LaTeX compiler."""

	COMMAND_COMPILER_PREFIX = "pdflatex -interaction=nonstopmode"
	COMMAND_CLEAN_PREFIX = "exiftool -all= -overwrite_original"

	command = None

	def __init__(self):
		"""Init function."""

		message.process("Latex")

	def compiler(self):
		"""Compiler LaTeX project."""

		message.step("Prepare")

		if self.check_file():
			return -1

		# Copy to tmp directory
		tmp_dir = utils.create_tmpdir("latex")
		message.message("Check copy to tmp directory")
		current_dir = os.getcwd()
		current_dir_name = os.path.basename(current_dir)

		# Copy to tmp directory
		command = f"cp -r {current_dir} {tmp_dir}"
		status, _ = utils.run_command(command.split())
		if status:
			message.error("Don't copy to tmp directory")
			return -2

		# Go to directory
		os.chdir(tmp_dir+"/"+current_dir_name)

		# Compiler
		message.step("Compile")
		if self.compiler_latex():
			return -3

		# Move pdf
		message.step("After")
		dest = "/tmp/"
		if config.options.actions.save:
			message.message("Save pdf")
			dest = f"{current_dir}/"
		else:
			message.message("Move pdf to /tmp")
		command = (
			f"mv {tmp_dir}/{current_dir_name}/{config.options.file}.pdf {dest}"
		)
		status, _ = utils.run_command(command.split())
		if status:
			message.error("Don't move pdf file")
			return -4

		return 0

	def check_file(self):
		"""Check main tex file."""

		message.message("Check file")
		# Search file
		if not config.options.file:
			self.__search_main_latex()

		if not config.options.file:
			message.error("Don't found any tex file")
			return -1

		# Check file
		if not Path(config.options.file).is_file():
			message.error("Don't found any file")
			return -2

		# Check extension
		file = os.path.splitext(config.options.file)
		if file[1] != ".tex":
			message.error("The file isn't tex")
			return -3

		# Save only name without extension
		config.options.file = file[0]

		return 0

	def compiler_latex(self):
		"""Compile latex project."""

		message.message("Compile")
		command = f"{self.COMMAND_COMPILER_PREFIX} {config.options.file}"
		self.command = command.split()
		status, _ = utils.run_command(self.command)
		if status:
			message.error("Compile latex")
			return -3

		# Biber
		if config.options.options.biber:
			if self.compiler_biber():
				return -4

		# Delete metadata
		message.message("Delete pdf metadata")
		command = f"{self.COMMAND_CLEAN_PREFIX} {config.options.file}.pdf"
		status, _ = utils.run_command(command.split())
		if status:
			message.error("Don't delete metadata")
			return -6
		return 0

	def compiler_biber(self):
		"""
		Compiler to user biber and recompiler the project 2 times.
		"""

		message.message("Run biber and recompile")
		command_biber = f"biber {config.options.file}"

		message.message("Run biber")
		status, _ = utils.run_command(command_biber.split())
		if status:
			message.error("Run biber")
			return -1
		message.message("Compiler")
		status, _ = utils.run_command(self.command)
		if status:
			message.error("Compile latex")
			return -2
		message.message("Compiler")
		status, _ = utils.run_command(self.command)
		if status:
			message.error("Compile latex")
			return -3
		return 0

	def __search_main_latex(self):
		"""Search main latex file."""

		message.message("Search main latex file")

		for element in list(Path().glob('*.tex')):
			if os.path.isfile(element):
				config.options.file = str(element)
