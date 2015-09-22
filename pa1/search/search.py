# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    removedStates = set()
    startState = (problem.getStartState(), [])
    stack = util.Stack()
    stack.push(startState)
    while not stack.isEmpty():
        state, path = stack.pop()
        if not state in removedStates:
            removedStates.add(state)
            if problem.isGoalState(state):
                return path

            for successorState, successorDirection, successorCost in \
            problem.getSuccessors(state):
                stack.push((successorState, path + [successorDirection]))

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    goalState = None
    startState = problem.getStartState()
    parentStateDict = { startState: None }
    parentDirectionDict = { startState: None }
    queue = util.Queue()
    queue.push(startState)
    while not queue.isEmpty():
        state = queue.pop()
        if problem.isGoalState(state):
            goalState = state
            break

        successors = problem.getSuccessors(state)
        for successor in successors:
            successorState = successor[0]
            successorDirection = successor[1]
            successorCost = successor[2]
            if not successorState in parentStateDict:
                parentStateDict[successorState] = state
                parentDirectionDict[successorState] = successorDirection
                queue.push(successorState)

    if goalState:
        actionList = []
        state = goalState
        while cmp(state, startState) != 0:
            actionList.append(parentDirectionDict[state])
            state = parentStateDict[state]

        actionList.reverse()
        return actionList
    else:
        return None

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    goalState = None
    startState = problem.getStartState()
    parentStateDict = { startState: None }
    parentDirectionDict = { startState: None }
    stateCostDict = { startState: 0 }
    priorityQueue = util.PriorityQueue()
    priorityQueue.push(startState, stateCostDict[startState])
    removedStates = set()
    while not priorityQueue.isEmpty():
        state = priorityQueue.pop()
        if not state in removedStates:
            removedStates.add(state)
            if problem.isGoalState(state):
                goalState = state
                break

            successors = problem.getSuccessors(state)
            for successor in successors:
                successorState = successor[0]
                successorDirection = successor[1]
                successorCost = successor[2]
                if (not successorState in removedStates) and \
                (not successorState in stateCostDict or successorCost + \
                stateCostDict[state] < stateCostDict[successorState]):
                    parentStateDict[successorState] = state
                    parentDirectionDict[successorState] = successorDirection
                    stateCostDict[successorState] = successorCost + \
                    stateCostDict[state]
                    priorityQueue.push(successorState, \
                    stateCostDict[successorState])

    if goalState:
        actionList = []
        state = goalState
        while cmp(state, startState) != 0:
            actionList.append(parentDirectionDict[state])
            state = parentStateDict[state]

        actionList.reverse()
        return actionList
    else:
        return None

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    removedStates = set()
    startState = (problem.getStartState(), heuristic(problem.getStartState(), \
    problem), [])
    priorityQueue = util.PriorityQueue()
    priorityQueue.push(startState, startState[1])
    while not priorityQueue.isEmpty():
        state, oldCost, path = priorityQueue.pop()
        if not state in removedStates:
            removedStates.add(state)
            if problem.isGoalState(state):
                return path

            for successorState, successorDirection, successorCost in \
            problem.getSuccessors(state):
                newCost = oldCost + successorCost
                priorityQueue.push((successorState, newCost, path + \
                [successorDirection]), newCost + heuristic(successorState, \
                problem))


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
