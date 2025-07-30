'''
File: test_StateMachine.py
Created Date: Sunday, July 0th 2020, 12:17:58 am
Author: Zentetsu

----

Last Modified: Fri Oct 23 2020
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
2020-09-17	Zen	Adding test for encapsulated state
2020-09-12	Zen	Adding test for JSON file
2020-09-10	Zen	Adding test to load and run StateMachine from JSON file
2020-09-10	Zen	Adding test to check if the StateMachine works with a single state
'''


# from context import State, Transition, StateMachine
from CorState.State import State
from CorState.Transition import Transition
from CorState.StateMachine import StateMachine
from math import inf

def test_createStateInstance():
    print("Create State Instance:", end=" ")
    try:
        s = State()
        assert type(s.getID()) == int
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_createTransitionInstance():
    print("Create Transition Instance:", end=" ")
    try:
        t = Transition()
        assert type(t.getID()) == int
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_createStateMachineInstance():
    print("Create StateMachine Instance:", end=" ")
    try:
        sm = StateMachine("test")
        assert sm.getName() == "test"
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_addStateToSM():
    print("Add State To StateMachine Instance:", end=" ")
    try:
        sm = StateMachine("test")
        s = State()
        sm.addState(s)
        assert len(sm.getStates()) == 1
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_addTransitionToSM():
    print("Add Transition To StateMachine Instance:", end=" ")
    try:
        sm = StateMachine("test")
        t = Transition()
        t.setInOutID(None, 0)
        sm.addTransition(t)
        assert len(sm.getTransitions()) == 1
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def test_simpleSM():
    print("Create Simple StateMachine:", end=" ")
    try:
        sm = StateMachine("test")
        s = State()
        t1 = Transition()
        t1.setInOutID(None, s.getID())
        t2 = Transition()
        t2.setInOutID(s.getID(), None)
        sm.addState(s)
        sm.addTransition(t1)
        sm.addTransition(t2)
        assert len(sm.getStates()) == 1 and len(sm.getTransitions()) == 2
        print("SUCCESSED")
    except:
        print("FAILED")
        assert False

def ev():
    return True

def act():
    pass

def test_runSimpleSM():
    print("Run Simple StateMachine:", end=" ")
    try:
        sm = StateMachine("test")
        s = State()
        s.addAction(act)
        t1 = Transition()
        t1.setInOutID(inf, s.getID())
        t1.addEvaluation(ev)
        t2 = Transition()
        t2.setInOutID(s.getID(), -inf)
        t2.addEvaluation(ev)
        sm.addState(s)
        sm.addTransition(t1)
        sm.addTransition(t2)
        assert len(sm.getStates()) == 1 and len(sm.getTransitions()) == 2
        sm.start()
        print("SUCCESSED")
        assert True
    except:
        print("FAILED")
        assert False

def test_loadJSONFile():
    print("load JSON file:", end=" ")
    try:
        sm = StateMachine("test")
        sm.loadJSON("./tests/test.json")
        sm.start()
        print("SUCCESSED")
        assert True
    except:
        print("FAILED")
        assert False

def test_loadJSONFile2():
    print("load JSON file 2:", end=" ")
    try:
        sm = StateMachine("test")
        sm.loadJSON("./tests/StateMachine.json")
        sm.start()
        print("SUCCESSED")
        assert True
    except:
        print("FAILED")
        assert False

def test_runEncSM():
    print("Run Encapsuled StateMachine:", end=" ")
    try:
        sm = StateMachine("test2")
        sm.loadJSON("./tests/test2.json")
        sm.start()
        print("SUCCESSED")
        assert True
    except:
        print("FAILED")
        assert False

print("-"*10)
test_createStateInstance()
test_createTransitionInstance()
test_createStateMachineInstance()
test_addStateToSM()
test_addTransitionToSM()
test_simpleSM()
test_runSimpleSM()
test_loadJSONFile()
test_loadJSONFile2()
test_runEncSM()
print("-"*10)