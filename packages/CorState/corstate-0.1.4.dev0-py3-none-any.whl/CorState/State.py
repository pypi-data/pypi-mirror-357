"""
File: State.py
Created Date: Sunday, July 0th 2020, 12:13:46 am
Author: Zentetsu

----

Last Modified: Thu Dec 26 2024
Modified By: Zentetsu

----

Project: CorState
Copyright (c) 2020 Zentetsu

----

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

----

HISTORY:
2020-09-17	Zen	Adding encapsulated state
2020-09-12	Zen	Updating init by JSON file
2020-09-12	Zen	Updating some comments
2020-09-11	Zen	Updating import module
2020-09-10	Zen	Refactoring the State structure
"""  # noqa

from .CorStateError import *
import importlib
import sys, os


class State:
    """State class."""

    __nb_state = 0

    def __init__(self) -> None:
        """Class constructor."""
        self.__id = State.__nb_state
        State.__nb_state = State.__nb_state + 1

        self.__action = None
        self.__encapsulation = False

    def getID(self) -> int:
        """Return the State ID.

        Returns:
            int: State ID

        """
        return self.__id

    def initBySFF(self, sff: dict, module: str) -> None:
        """Initialize a State from a JSON file.

        Args:
            sff (dict): state from file
            module (str): module information

        """
        sys.path.append(os.path.dirname(module))
        module_name = os.path.splitext(os.path.basename(module))[0]
        self.__mod = importlib.import_module(module_name)

        self.__id = sff["id"]
        self.__action = getattr(self.__mod, sff["action"])
        self.__encapsulation = sff["encapsulation"]

    def addAction(self, action: callable) -> None:
        """Add action to this state.

        Args:
            action ([type]): action that will be executed by this state

        """
        self.__action = action

    def run(self) -> None:
        """Run the action defined for this state."""
        self.__action()

    def setEncapsulation(self, value: bool) -> None:
        """Set the encapsulation value.

        Args:
            value (bool): The encapsulation value to set.

        """
        self.__encapsulation = value

    def getEncapsulation(self) -> bool:
        """Get the encapsulation value.

        Returns:
            bool: The encapsulation value.

        """
        return self.__encapsulation

    def __repr__(self) -> str:
        """Redefined method to print value of the State class instance.

        Returns:
            str: printable value of State class instance

        """
        s = "State id: " + str(self.__id)

        return s
