# See LICENSE file for copyright and license details.
"""Mbed submodule."""
import os
from pathlib import Path

from scompiler.message import message
from scompiler.options import config
from scompiler.utils import create_tmpdir, run_command


class TypeMbed():
	"""Main Mbed compiler."""

	PKG_DIR = "/tmp/scompiler-test-py"
	COMMAND_VENV = "python -m venv .venv"
	COMMAND_BUILD_PREFIX = f"{PKG_DIR}/.venv/bin"

	def __init__(self):
		"""Init function."""

		message.process("Mbed")

	def compiler(self):
		"""Compiler Mbed project."""

		message.step("Prepare")
		if not config.options.options.nucleo:
			message.error("Specific the STM target")
			return -1

		# Copy to tmp directory
		tmp_dir = create_tmpdir("mbed")
		message.message("Check copy to tmp directory")

		if not os.path.islink("cmake_build"):
			link = Path("cmake_build")
			target = Path(f"{tmp_dir}/")
			link.symlink_to(target)

		if self.create_venv():
			return -2

		# Compiler
		message.step("Compile")
		command = (
			f"{self.COMMAND_BUILD_PREFIX}/mbed-tools compile "
			f"-m {config.options.options.nucleo} -t GCC_ARM"
		)

		status, info = run_command(command.split())
		if status:
			message.error("Compile")
			print(f"{info.stderr.decode('utf-8')}")
			return -3

		# Copy the output
		message.step("After")
		dest = "/tmp"
		if config.options.actions.save:
			message.message("Save bin")
			dest = "."
		else:
			message.message("Move bin to /tmp")

		current_dir_name = os.path.basename(os.getcwd())
		command = (
			f"cp cmake_build/{config.options.options.nucleo}/"
			"develop/GCC_ARM/*.bin "
			f"{dest}/stm_{current_dir_name}.bin"
		)

		status, info = run_command(command, shell=True)
		if status:
			message.error("Copy")
			print(f"{info.stderr.decode('utf-8')}")
			return -3

		return 0

	def create_venv(self):
		"""Create venv."""
		message.message("Create venv")
		status, info = run_command(self.COMMAND_VENV.split())
		if status:
			message.error(f"Run: {info.stderr.decode('utf-8')}")
			return -1

		message.message("Install mbed-tools")
		command = f"{self.COMMAND_BUILD_PREFIX}/pip install mbed-tools"
		status, info = run_command(command.split())
		if status:
			message.error("Install mbed-tools")
			print(f"{info.stderr.decode('utf-8')}")
			return -2
		return 0
