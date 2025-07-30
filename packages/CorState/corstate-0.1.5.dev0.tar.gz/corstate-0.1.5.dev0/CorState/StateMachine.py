"""
File: StateMachine.py
Created Date: Thursday, July 4th 2020, 10:01:03 pm
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
2020-10-10	Zen	Updating JSON file loading
2020-09-18	Zen	Using inf value for first and last transition
2020-09-17	Zen	Adding encapsulated state
2020-09-12	Zen	Updating init by JSON file
2020-09-12	Zen	Updating some comments
2020-09-10	Zen	Generating StateMachine from JSON file
2020-09-10	Zen	Refactoring the StateMachine structure
"""  # noqa

import os
import json
from math import inf
from typing import Union
from .State import State
from .Transition import Transition
from .CorStateError import *


class StateMachine:
    """StateMachine class."""

    def __init__(self, name: str) -> None:
        """Class constructor."""
        self.__name = name
        self.__states = {}
        self.__transitions = {}
        self.__states_stack = []

        self.__data = None

    def getName(self) -> str:
        """Return the StateMachine name.

        Returns:
            str: StateMachine name

        """
        return self.__name

    def start(self) -> None:
        """Launch the state StateMachine."""
        self.__checkStateMachineIntegrity()

        _stateID = inf
        _breaked = True
        _next_transition = False

        while _breaked:
            _breaked = False

            for tr in self.__transitions.keys():
                # valid = (
                #     (
                #         self.__transitions[tr].getInOutID()[0] == _stateID
                #         or -self.__transitions[tr].getInOutID()[0] == _stateID
                #         and _stateID != -inf
                #     )
                #     and self.__transitions[tr].evaluate()
                #     and _next_transition is False
                # )

                if (
                    self.__transitions[tr].getInOutID()[0] == _stateID
                    and self.__transitions[tr].evaluate()
                    and _next_transition is False
                ):
                    _stateID = self.__transitions[tr].getInOutID()[1]

                    _breaked = True
                    break
                elif (
                    -self.__transitions[tr].getInOutID()[0] == _stateID
                    and _stateID != -inf
                    and self.__transitions[tr].evaluate()
                    and _next_transition is False
                ):
                    _stateID = self.__transitions[tr].getInOutID()[1]

                    _breaked = True
                    break
                elif (
                    self.__transitions[tr].getInOutID()[0] == -_stateID
                    and _next_transition
                ):
                    _stateID = self.__transitions[tr].getInOutID()[1]
                    _next_transition = False

                    _breaked = True
                    break
                elif (
                    self.__transitions[tr].getInOutID()[0] in self.__states_stack
                    and self.__transitions[tr].evaluate()
                ):
                    _stateID = self.__transitions[tr].getInOutID()[1]

                    while self.__transitions[tr].getInOutID()[0] in self.__states_stack:
                        self.__states_stack.pop()

                    _breaked = True
                    break

            if _breaked:
                if _stateID != -inf and _stateID >= 0 and _next_transition is False:
                    if self.__states[_stateID].getEncapsulation():
                        self.__states_stack.append(_stateID)

                    self.__states[_stateID].run()
                elif _stateID != -inf and _stateID < 0:
                    _next_transition = True

        if _stateID != -inf:
            print("ERROR")

    def addState(
        self, value: Union[dict, State, None] = None, path: str = None
    ) -> None:
        """Add a state to the StateMachine.

        Args:
            value ([type], optional): Value that will initialize a new State. Defaults to None.
            path (str, optional): Path to the called function for the StateMachine. Defaults to None.

        Raises:
            SMAddingStateError: raise an error when the value can't be casted into a State.

        """
        if type(value) is dict:
            _state = State()
            _state.initBySFF(value, path)
        elif type(value) is State:
            _state = value
        elif value is None:
            _state = State()
            _state.addAction(value)
        else:
            raise SMAddingStateError

        self.__states[_state.getID()] = _state

    def removeState(self, state_id: int) -> None:
        """Remove a state from the StateMachine.

        Args:
            state_id (int): state id

        """
        del self.__states[state_id]

    def getStates(self) -> dict:
        """Return the States dict.

        Returns:
            dict: States dict

        """
        return self.__states

    def addTransition(
        self, value: Union[dict, Transition, None] = None, path: str = None
    ) -> None:
        """Add a transition to the StateMachine.

        Args:
            value ([type], optional): Value that will initialize a new Transition. Defaults to None.
            path (str, optional): Path to the called function for the StateMachine. Defaults to None.

        Raises:
            SMAddingStateError: raise an error when the value can't be casted into a Transition.

        """
        if type(value) is dict:
            _transition = Transition()
            _transition.initByTFF(value, path)
        elif type(value) is Transition:
            _transition = value
        elif value is None:
            _transition = Transition()
            _transition.addEvaluation(value)
        else:
            raise SMAddingTransitionError

        self.__transitions[_transition.getID()] = _transition

    def removeTransition(self, transition_id: int) -> None:
        """Remove a Transition from the Transition Machine.

        Args:
            transition_id (int): Transition id

        """
        del self.__transitions[transition_id]

    def getTransitions(self) -> dict:
        """Return the Transitions dict.

        Returns:
            dict: Transition dict

        """
        return self.__transitions

    def __checkStateMachineIntegrity(self) -> None:
        """Check the integrity of the StateMachine."""
        if [
            self.__transitions[t].getInOutID()[0] == inf
            and self.__transitions[t].getInOutID()[1] in self.__states.keys()
            for t in self.__transitions.keys()
        ].count(True) != 1:
            raise SMIntegrityError("Initial")

        if [
            self.__transitions[t].getInOutID()[1] == -inf
            and self.__transitions[t].getInOutID()[0] in self.__states.keys()
            for t in self.__transitions.keys()
        ].count(True) != 1:
            raise SMIntegrityError("Final")

    def __checkJSONIntegrity(self) -> None:
        """Check the JSON file integrity.

        Raises:
            SMJSONIntegrityError: raise an error when an element is not present into the JSON file

        """
        if not all([k in self.__data.keys() for k in ["path", "StateMachine"]]):
            raise SMJSONIntegrityError(
                "module__name, path and/or StateMachine values of JSON file"
            )

        if not all(
            [
                k in self.__data["StateMachine"].keys()
                for k in ["Variable", "State", "Transition"]
            ]
        ):
            raise SMJSONIntegrityError(
                "Variable, State and/or Transition values of StateMachine"
            )

        if len(self.__data["StateMachine"]["State"].keys()) > 0 and not all(
            [
                k in self.__data["StateMachine"]["State"][s].keys()
                for k in ["id", "action", "encapsulation"]
                for s in self.__data["StateMachine"]["State"].keys()
            ]
        ):
            raise SMJSONIntegrityError("id and/or action values of a specific State")

        if not all(
            [
                t in self.__data["StateMachine"]["Transition"].keys()
                for t in ["in", "out"]
            ]
        ):
            raise SMJSONIntegrityError("in and/or out values of Transition")

        if not all(
            [
                k in self.__data["StateMachine"]["Transition"][t].keys()
                for k in ["id_in", "id_out", "evaluation"]
                for t in self.__data["StateMachine"]["Transition"].keys()
            ]
        ):
            raise SMJSONIntegrityError(
                "id_in, id_out and/or evaluation of a specific Transition"
            )

    def __generateStateMachineStructure(self) -> None:
        """Generate StateMachine structure.

        Raises:
            FileNotFoundError: raise an error the file leading to the functions definition doesn't exist

        """
        if not os.path.isfile(self.__data["path"]):
            file_sm = open(self.__data["path"], "w+")
            # os.mknod(self.__data['path'])
            # raise FileNotFoundError
        else:
            file_sm = open(self.__data["path"], "r+")

        lines = file_sm.readlines()

        for v in self.__data["StateMachine"]["Variable"].keys():
            if True not in [v in l for l in lines]:
                file_sm.write(
                    v + " = " + str(self.__data["StateMachine"]["Variable"][v]) + "\n"
                )

        for s in self.__data["StateMachine"]["State"].keys():
            if True not in [
                "def " + self.__data["StateMachine"]["State"][s]["action"] in l
                for l in lines
            ]:
                file_sm.write(
                    "def "
                    + self.__data["StateMachine"]["State"][s]["action"]
                    + "():\n\t#TODO\n\tpass\n\n"
                )

            # self.addState(self.__data["StateMachine"]["State"][s], self.__data["path"])

        for t in self.__data["StateMachine"]["Transition"].keys():
            if True not in [
                "def " + self.__data["StateMachine"]["Transition"][t]["evaluation"] in l
                for l in lines
            ]:
                file_sm.write(
                    "def "
                    + self.__data["StateMachine"]["Transition"][t]["evaluation"]
                    + "():\n\t#TODO\n\tpass\n\n"
                )

            # self.addTransition(self.__data["StateMachine"]["Transition"][t], self.__data["path"])

        file_sm.close()

        for s in self.__data["StateMachine"]["State"].keys():
            self.addState(self.__data["StateMachine"]["State"][s], self.__data["path"])

        for t in self.__data["StateMachine"]["Transition"].keys():
            self.addTransition(
                self.__data["StateMachine"]["Transition"][t], self.__data["path"]
            )

    def loadJSON(self, path: str) -> None:
        """Load JSON file."""
        json_file = open(path)

        self.__data = json.load(json_file)
        json_file.close()

        if "SM" not in self.__data.keys():
            raise SMJSONIntegrityError("SM key not in JSON file")

        self.__data = self.__data["SM"]

        self.__checkJSONIntegrity()
        self.__generateStateMachineStructure()

    def __dumpJSON(self, name: str) -> None:
        """Save the StateMachine to a JSON file."""
        pass

    def __repr__(self) -> str:
        """Redefined method to print value of the StateMachine class instance.

        Returns:
            str: printable value of StateMachine class instance

        """
        s = "State Machine name: " + self.__name + "\n"

        for st in self.__states.keys():
            s += self.__states[st].__repr__() + "\n"

        for tr in self.__transitions.keys():
            s += self.__transitions[tr].__repr__() + "\n"

        return s
