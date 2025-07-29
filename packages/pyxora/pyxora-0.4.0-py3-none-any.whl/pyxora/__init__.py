# Copyright (C) 2025 ToniDevStuff
# This project is licensed under the MIT License.
# See LICENSE.txt for full details.

"""
A simple game engine made with Python and pygame-ce.
"""
from importlib.metadata import version as _version
__version__ = _version("pyxora")

__project__ = "pyxora"
__author__ = "ToniDevStuff"

__docformat__ = "google"
__license__ = "MIT"

from os import environ as _environ
from sys import version_info as _python_version

# We are going to print or draw it ourself
_environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
# import pymunk

pygame.init()

# Ensure compatibility
if not getattr(pygame, "IS_CE", False):
	raise ImportError("Pyxora supports only pygame-ce.")

debug: bool = True
"""
Flag var indicating whether debug mode is enabled.\n
Set it to `False` if you want to disable the extra debugging features.
"""

version: str = __version__
"""pyxora version"""
python_version: str = f"{_python_version[0]}.{_python_version[1]}.{_python_version[2]}"
"""@private Python version"""
pygame_version: str = pygame.version.ver
"""pygame version"""
sdl_version: str = f"{pygame.version.SDL[0]}.{pygame.version.SDL[1]}.{pygame.version.SDL[2]}"
"""SDL version"""
# pymunk_version: str = pymunk.version
"""pymunk version"""

from .wrapper import *
from .utils import asyncio,engine

# (Not ready)
# from .object import Object,ObjectScript,Objects
from .assets import Assets
from .display import Display
from .camera import Camera
from .scene import Scene
