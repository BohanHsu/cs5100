# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        currentGhostStates = currentGameState.getGhostStates()
        mazeWalls = currentGameState.getWalls()
        foodList = newFood.asList()
        capsulePositions = currentGameState.getCapsules()
        distanceToAllFoods = pacmanDistanceToTargets(newPos, foodList, mazeWalls)

        score = 0.0

        # don't want pacman keep stop
        if action == Directions.STOP:
            score -= 1

        # give credit for pacman if eat a bean
        eatBean = currentGameState.getNumFood() - \
        successorGameState.getNumFood() == 1
        if eatBean:
            score += 100

        # guide pacman to clostest food
        if (len(distanceToAllFoods) != 0):
            score -= min(distanceToAllFoods)

        # make pacman fear ghost
        def positionToInt(position):
            return (int(position[0]), int(position[1]))

        distanceToAllGhost = pacmanDistanceToTargets(newPos, map(lambda \
        ghostState: positionToInt(ghostState.getPosition()), \
        [newGhostStates[i] for i in range(len(newGhostStates)) if \
        newScaredTimes[i] == 0]), mazeWalls)

        if (len(distanceToAllGhost) != 0):
            distanceToClostestGhost = min(distanceToAllGhost)
            if (distanceToClostestGhost < 5):
                score -= (5 - distanceToClostestGhost) * 100

                # if pacman felt chased by ghost, try to find the capsule
                if (len(capsulePositions) != 0):
                    distanceToAllCapsules = pacmanDistanceToTargets(newPos, \
                    capsulePositions, mazeWalls)
                    distanceToClostestCapsule = min(distanceToAllCapsules)
                    score -= distanceToClostestCapsule * 80

        # try to capture eatable ghost to get 1000 points
        if (len([0 for ghostState in currentGhostStates if \
        ghostState.scaredTimer]) != 0):
            eatableGhosts = {newGhostStates[i].getPosition() : newScaredTimes[i] \
            for i in range(len(newGhostStates)) if newScaredTimes[i] != 0}
            eatableGhostPositions = [eatableGhostPos for eatableGhostPos, \
            scaredTime in eatableGhosts.iteritems()]
            eatableGhostScareTimes = [scaredTime for eatableGhostPos,
            scaredTime in eatableGhosts.iteritems()]

            distanceToAllEatableGhosts = pacmanDistanceToTargets(newPos,\
            map(lambda ghostPos: positionToInt(ghostPos), \
            eatableGhostPositions), mazeWalls)

            eatableGhosts = [(eatableGhostPositions[i], \
            eatableGhostScareTimes[i], distanceToAllEatableGhosts[i])for i in \
            range(len(eatableGhostPositions)) if \
            distanceToAllEatableGhosts[i] < eatableGhostScareTimes[i]]

            if (len(eatableGhosts) != 0):
                clostestEatableGhost = min(eatableGhosts, \
                key=lambda tuple: tuple[1])
                score -= (clostestEatableGhost[2]) * 5

        return score

def pacmanDistanceToTargets(source, targets, walls):
    removedStates = set()
    targetsDict = {target: -1 for target in targets}
    queue = util.Queue()
    queue.push((source, 0))
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while not queue.isEmpty():
        state, distance = queue.pop()
        if not state in removedStates:
            removedStates.add(state)

            if state in targetsDict and targetsDict[state] == -1:
                targetsDict[state] = distance

            if (len([k for k, v in targetsDict.iteritems() if v == -1]) == 0):
                return [targetsDict[target] for target in targets]

            def positionAdd(p1, p2):
                return (int(p1[0] + p2[0]), int(p1[1] + p2[1]))

            [queue.push(((nextx, nexty), distance + 1)) for nextx, nexty in \
            [positionAdd(state, action) for action in actions] if not \
            walls[nextx][nexty]]

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction

