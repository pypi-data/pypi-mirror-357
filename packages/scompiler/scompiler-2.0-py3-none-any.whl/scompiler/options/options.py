# See LICENSE file for copyright and license details.
"""Module to set configuration."""
# import os

from dataclasses import dataclass


@dataclass()
class OptionsActions:
	"""Actions options."""

	save: bool = False
	version: bool = False
	clear: bool = False


@dataclass()
class OptionsMode:
	"""Boolean options."""

	# LaTeX
	biber: bool = False
	# Mbed
	nucleo: str = None
	# Python
	package: bool = False


@dataclass()
class Options:
	"""Run options."""

	file_type: str = None
	file: str = None
	options: OptionsMode = None
	actions: OptionsActions = None
