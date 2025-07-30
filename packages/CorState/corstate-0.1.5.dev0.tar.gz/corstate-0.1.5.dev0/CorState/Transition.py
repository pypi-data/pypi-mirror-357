"""
File: Transition.py
Created Date: Sunday, August 0th 2020, 5:46:20 pm
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
2020-09-18	Zen	Catching inf value
2020-09-12	Zen	Updating init by JSON file
2020-09-12	Zen	Updating some comments
2020-09-11	Zen	Updating import module
2020-09-10	Zen	Refactoring the Transition structure
"""  # noqa

from .CorStateError import *
from math import inf
import importlib
import sys, os


class Transition:
    """Transition class."""

    __nb_transition = 0

    def __init__(self) -> None:
        """Class constructor."""
        self.__id = Transition.__nb_transition
        Transition.__nb_transition = Transition.__nb_transition + 1

        self.__ioID = None
        self.__evaluation = None

    def getID(self) -> int:
        """Return Transition ID.

        Returns:
            int: Transition ID

        """
        return self.__id

    def initByTFF(self, tff: dict, module: str) -> None:
        """Initialize a Transition from a JSON file.

        Args:
            tff (dict): state from file
            module (str): module information

        """
        sys.path.append(os.path.dirname(module))
        module_name = os.path.splitext(os.path.basename(module))[0]
        self.__mod = importlib.import_module(module_name)

        self.__id = tff["id"]

        if tff["id_in"] == "inf":
            self.__ioID = (inf, tff["id_out"])
        elif tff["id_out"] == "inf":
            self.__ioID = (tff["id_in"], -inf)
        else:
            self.__ioID = (tff["id_in"], tff["id_out"])

        self.__evaluation = getattr(self.__mod, tff["evaluation"])

    def setInOutID(self, ini: int, outi: int) -> None:
        """Initialize the in and out state id.

        Args:
            ini (int): in state id
            outi (int): out state id

        """
        self.__ioID = (ini, outi)

    from typing import Tuple

    def getInOutID(self) -> Tuple[int, int]:
        """Return the in and out state id.

        Returns:
            (int, int): tuple of in and out state id

        """
        return self.__ioID

    def addEvaluation(self, evaluation: callable) -> None:
        """Evaluate a condition to allow the State Machine to move to the next state.

        Args:
            evaluation ([type]): Function called to evaluate the possibility to move to the next state.

        """
        self.__evaluation = evaluation

    def evaluate(self) -> bool:
        """Run the evaluate function.

        Returns:
            bool: Evaluation result

        """
        return self.__evaluation()

    def __repr__(self) -> str:
        """Redefined method to print value of the Transition class instance.

        Returns:
            str: printable value of Transition class instance

        """
        s = "Transition id: " + self.__id.__repr__() + "; (in, out): " + self.__ioID.__repr__()

        return s
