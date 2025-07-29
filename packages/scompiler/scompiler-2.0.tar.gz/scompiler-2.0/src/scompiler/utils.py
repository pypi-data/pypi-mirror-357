# See LICENSE file for copyright and license details.
"""Module to utils functions."""
import subprocess
import os

from scompiler.message import message

TMP_DIR = "/tmp/scompiler"


def create_tmpdir(directory):
	"""Create tmp file."""

	tmp_dir = f"{TMP_DIR}/{directory}"

	# Create tmp directory
	message.step("Check tmp directory")
	if not os.path.isdir(tmp_dir):
		os.makedirs(tmp_dir)
	return tmp_dir


def run_command(command, shell=False, capture=True):
	"""Run a command."""

	try:
		if capture:
			info = subprocess.run(
				command,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				check=True,
				shell=shell
			)
		else:
			info = subprocess.run(
				command,
				shell=shell,
				check=True
			)
	except subprocess.CalledProcessError as e:
		return -1, e

	return 0, info


def clear_tmpdir():
	"""Clean tmp dir."""

	command = "rm -rf /tmp/scompiler"
	return run_command(command.split())
