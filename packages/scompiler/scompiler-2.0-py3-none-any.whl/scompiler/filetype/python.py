# See LICENSE file for copyright and license details.
"""Latex submodule."""
import os

from scompiler.message import message
from scompiler.options import config
from scompiler.run_script import RunScript
from scompiler.utils import create_tmpdir, run_command


class TypePython():
	"""Main Python compiler."""

	PKG_DIR = "/tmp/scompiler-test-py"
	COMMAND_VENV = f"python -m venv {PKG_DIR}/.venv"
	COMMAND_BUILD_PREFIX = f"{PKG_DIR}/.venv/bin"

	file = ""
	file_name = ""
	tmp_dir = None
	current_dir = ""
	current_dir_name = ""

	def __init__(self):
		"""Init function."""

		message.process("Python")

	def compiler(self):
		"""Compiler Python project."""

		if config.options.options.package:
			return self.run_pkg()
		return self.run_script()

	def run_pkg(self):
		"""Run python script."""

		message.process("Python package")

		message.step("Prepare")

		# Copy to tmp directory
		message.message("Copy to tmp directory")

		self.current_dir = os.getcwd()
		self.current_dir_name = os.path.basename(self.current_dir)
		self.tmp_dir = create_tmpdir("python")

		command = f"cp -fr {self.current_dir} {self.tmp_dir}"
		status, info = run_command(command.split())
		if status:
			message.error(f"Don't copy to tmp directory {info}")
			return -2

		# Go to pkg directory
		os.chdir(f"{self.tmp_dir}/{self.current_dir_name}")

		# Make venv
		message.message("Create venv directory")
		if not os.path.isdir(self.PKG_DIR):
			os.makedirs(self.PKG_DIR)

		message.message("Create venv")
		status, info = run_command(self.COMMAND_VENV.split())
		if status:
			message.error(f"Run: {info.stderr.decode('utf-8')}")
			return -3

		# Install base package
		message.step("Install packages")

		message.message("Install build")
		command = f"{self.COMMAND_BUILD_PREFIX}/pip install build"
		status, info = run_command(command.split())
		if status:
			message.error("Install package")
			print(f"{info.stderr.decode('utf-8')}")
			return -4

		message.message("Build package")
		command = f"{self.COMMAND_BUILD_PREFIX}/python -m build"
		status, info = run_command(command.split())
		if status:
			message.error("Install package")
			print(f"{info.stderr.decode('utf-8')}")
			return -5

		message.message("Install package")
		command = (
			f"{self.COMMAND_BUILD_PREFIX}/pip "
			f"install --force-reinstall dist/*.whl"
		)
		status, info = run_command(command, shell=True)
		if status:
			message.error("Install package")
			print(f"{info.stderr.decode('utf-8')}")
			return -6

		message.message("Success!!!")
		return 0

	def run_script(self):
		"""Run python script."""

		message.process("Python script")
		run_script = RunScript("python", ".py")
		return run_script.run_script()
