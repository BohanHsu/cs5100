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
        def terminalTest(gameState, depth):
            return gameState.isWin() or gameState.isLose() or depth >= self.depth

        def minimaxDecision(gameState):
            v = -float('inf')
            selectedAction = None
            actions = gameState.getLegalActions(0)
            for action in actions:
                prev = v
                v = max(minValue(gameState.generateSuccessor(0, action), 0, 1), v)
                if v > prev:
                    selectedAction = action

            return selectedAction

        def maxValue(gameState, depth):
            agentIndex = 0
            if terminalTest(gameState, depth):
                return self.evaluationFunction(gameState)

            v = -float('inf')
            actions = gameState.getLegalActions(agentIndex)
            for action in actions:
                v = max(minValue(gameState.generateSuccessor(0, action), depth, 1), v)

            return v

        def minValue(gameState, depth, agentIndex):
            if terminalTest(gameState, depth):
                return self.evaluationFunction(gameState)

            v = float('inf')
            actions = gameState.getLegalActions(agentIndex)
            if agentIndex == gameState.getNumAgents() - 1:
                for action in actions:
                    v = min(maxValue(gameState.generateSuccessor(agentIndex, action), depth + 1), v)
            else:
                for action in actions:
                    v = min(minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1), v)

            return v

        return minimaxDecision(gameState)

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """
    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def terminalTest(gameState, depth):
            return gameState.isWin() or gameState.isLose() or depth >= self.depth

        def alphaBetaDecision(gameState):
            v = -float('inf')
            selectedAction = None
            alpha = -float('inf')
            beta = float('inf')
            actions = gameState.getLegalActions(0)
            for action in actions:
                prev = v
                v = max(minValue(gameState.generateSuccessor(0, action), 0, 1, alpha, beta), v)
                if v > prev:
                    selectedAction = action

                if v > beta:
                    return selectedAction

                alpha = max(alpha, v)

            return selectedAction

        def maxValue(gameState, depth, alpha, beta):
            agentIndex = 0
            if terminalTest(gameState, depth):
                return self.evaluationFunction(gameState)

            v = -float('inf')
            actions = gameState.getLegalActions(agentIndex)
            for action in actions:
                v = max(minValue(gameState.generateSuccessor(0, action), depth, 1, alpha, beta), v)
                if v > beta:
                    return v

                alpha = max(alpha, v)

            return v

        def minValue(gameState, depth, agentIndex, alpha, beta):
            if terminalTest(gameState, depth):
                return self.evaluationFunction(gameState)

            v = float('inf')
            actions = gameState.getLegalActions(agentIndex)
            if agentIndex == gameState.getNumAgents() - 1:
                for action in actions:
                    v = min(maxValue(gameState.generateSuccessor(agentIndex, action), depth + 1, alpha, beta), v)
                    if v < alpha:
                        return v

                    beta = min(beta, v)
            else:
                for action in actions:
                    v = min(minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1, alpha, beta), v)
                    if v < alpha:
                        return v

                    beta = min(beta, v)

            return v

        return alphaBetaDecision(gameState)

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
        def terminalTest(gameState, depth):
            return gameState.isWin() or gameState.isLose() or depth >= self.depth

        def expectimaxDecision(gameState):
            v = -float('inf')
            selectedAction = None
            actions = gameState.getLegalActions(0)
            for action in actions:
                prev = v
                v = max(expectValue(gameState.generateSuccessor(0, action), 0, 1), v)
                if v > prev:
                    selectedAction = action

            return selectedAction

        def maxValue(gameState, depth):
            agentIndex = 0
            if terminalTest(gameState, depth):
                return self.evaluationFunction(gameState)

            v = -float('inf')
            actions = gameState.getLegalActions(agentIndex)
            for action in actions:
                v = max(expectValue(gameState.generateSuccessor(0, action), depth, 1), v)

            return v

        def expectValue(gameState, depth, agentIndex):
            if terminalTest(gameState, depth):
                return self.evaluationFunction(gameState)

            weight = 0.0
            count = 0
            actions = gameState.getLegalActions(agentIndex)
            if agentIndex == gameState.getNumAgents() - 1:
                for action in actions:
                    #v = min(maxValue(gameState.generateSuccessor(agentIndex, action), depth + 1), v)
                    weight += maxValue(gameState.generateSuccessor(agentIndex, action), depth + 1)
                    count += 1
            else:
                for action in actions:
                    weight += expectValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1)
                    count += 1

            return weight / count

        return expectimaxDecision(gameState)

def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: 
      First, pacman will get all information about food, ghost, and capsule in
      the current state, then pacman will do a BFS to find distance to nearest
      food, nearest ghost, nearest ghost that can be eat by pacman, and nearest
      capsule.
      The score of a state is based on the following factors:
      1) number of food left, the less the food, the higher the score
      2) number of capsule, the less the capsule, the higher the score
      3) number of ghost, the less the ghost, the higher the score
      4) distance to nearest food, the shorter the distance, the higher the
         score
      5) distance to nearest capsule, the shorter the distance, the higher the
         score
      6) distance to nearest ghost is the ghost is less than five steps to reach
         pacman, the longer the distance, the higher the score
      7) distance to nearest eatable ghost, the shorter the distance, the higher
         the score
      8) whether the state is winning state, the winning state will achieve a
         very score other than non-winning state

    """
    "*** YOUR CODE HERE ***"
    score = 0.0
    foodList = currentGameState.getFood().asList()
    numOfFoodLeft = len(foodList)
    mazeWalls = currentGameState.getWalls()
    ghostStates = currentGameState.getGhostStates()
    numOfGhosts = len(ghostStates)
    ghostPositions = [ghostState.getPosition() for ghostState in ghostStates if ghostState.scaredTimer == 0]
    eatableGhostPositions = {ghostState.getPosition(): ghostState.scaredTimer for ghostState in ghostStates if ghostState.scaredTimer > 0}
    numOfEatableGhost = len(eatableGhostPositions)
    capsuleList = currentGameState.getCapsules()
    numOfCapsule = len(capsuleList)
    currentPosition = currentGameState.getPacmanPosition()

    def pacmanSearch(position, foodPositions, ghostPositions, eatableGhostPositions, capsulePositions, mazeWalls):
        food = None
        ghost = None
        eatableGhost = None
        capsule = None
        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        def shouldContinue():
            return (food is None) or (ghost is None) or (eatableGhost is None) or (capsule is None)

        def positionAdd(p1, p2):
            return (int(p1[0] + p2[0]), int(p1[1] + p2[1]))

        exploredPositions = set()
        queue = util.Queue()
        queue.push((position, 0, False))

        while not queue.isEmpty():
            if not shouldContinue():
                break

            curNode = queue.pop()
            curPos = curNode[0]
            if not curPos in exploredPositions:
                exploredPositions.add(curPos)

                if food is None and curPos in foodPositions and not curNode[2]:
                    food = curNode[1]

                if ghost is None and curPos in ghostPositions:
                    ghost = curNode[1]

                if eatableGhost is None and curPos in eatableGhostPositions and not curNode[2] and eatableGhostPositions[curPos] > curNode[1]:
                    eatableGhost = curNode[1]

                if capsule is None and curPos in capsulePositions and not curNode[2]:
                    capsule = curNode[1]

                for newPos in [positionAdd(action, curPos) for action in actions]:
                    if not mazeWalls[newPos[0]][newPos[1]]:
                        if newPos in ghostPositions:
                            queue.push((newPos, curNode[1] + 1, True))
                        else:
                            queue.push((newPos, curNode[1] + 1, curNode[2]))

        return [food, ghost, eatableGhost, capsule]

    searchResult = pacmanSearch(currentPosition, foodList, ghostPositions, eatableGhostPositions, capsuleList, mazeWalls)

    score -= numOfFoodLeft * 101
    score -= numOfCapsule * 201
    score -= numOfGhosts * 203

    foodDist = searchResult[0]
    ghostDist = searchResult[1]
    eatableGhostDict = searchResult[2]
    capsuleDist = searchResult[3]

    if not foodDist is None:
        score -= 2 * foodDist

    if not capsuleDist is None:
        score -= capsuleDist * 3

    if not ghostDist is None and ghostDist <= 4:
        score -= (5 - ghostDist) * 502

    if not eatableGhostDict is None:
        score -= eatableGhostDict * 4

    if currentGameState.isWin():
        score += 1000001

    return score

# Abbreviation
better = betterEvaluationFunction

