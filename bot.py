#!/bin/env python2.7

# Have fun if you read this ****

import sys

import json
import random

class Battleship:

    def __init__(self, jsonFile):

        self.command = jsonFile["cmd"]

		# In this case, nothing to compute, just return the initialized board
        if self.command != "move":
            return

		# Player name
        self.player = jsonFile["you"]
		# List of previous moves
        self.moves = jsonFile["moves"]
		# List of target that have been shot
        self.hit = jsonFile["hit"]
		# List of missed shots
        self.missed = jsonFile["missed"]
		# List of destroyed ships
        self.destroyed = jsonFile["destroyed"]
        for index, length in enumerate(self.destroyed):
            self.destroyed[index] = int(length)

		# Biggest ship alive
        self.biggestNotDestroyed = 5
        if 5 in self.destroyed:
            self.biggestNotDestroyed = 4
        if 4 in self.destroyed:
            if (self.biggestNotDestroyed == 4):
                self.biggestNotDestroyed = 3
        if 3 in self.destroyed:
            if (self.biggestNotDestroyed == 3):
                self.biggestNotDestroyed = 2
		# Variables to test if ships are found
        self.ship2IsFound = False
        self.ship3IsFound = False
        self.ship4IsFound = False
        self.ship5IsFound = False

		# Lists that are used to compute next move
		# List of previous moves
        self.intMoves = [int(x) for x in self.moves]
		# List of my previous moves
        self.intMyTurns = []
        for index in range(0, len(self.intMoves)):
            if (self.intMoves[index] / 1000 == self.player):
                self.intMyTurns.append(self.intMoves[index] % 1000)
		# List of my previous moves
        self.intMyMoves = [(x / 10) for x in self.intMyTurns]
		# List of my previous hits
        self.intMyHits = []
        for index in range(0, len(self.intMyTurns)):
            if (self.intMyTurns[index] % 10 > 2):
                self.intMyHits.append(self.intMyTurns[index] / 10)
		# List of missed shots
        self.missedAndDestroyed = [int(x) for x in self.missed]
		# List of missed shots
        self.hitNotDestroyed = [int(x) for x in self.hit]
		# List of empty cells
        self.emptyCells = []
        self.__initEmptyCells()

		# Destroyed ship locations
        self.__findDestroyedShips()

		# Initializes probabilities for each cell
        self.chancesToHaveShips = {}
        self.__initChancesToHaveShips()

		# Function that computes chances to hit a target for each cell
        self.__computeChances()


    def __initEmptyCells(self):

        for row in range(0,8):
            for col in range(0,8):
                if (not (10*row + col in self.missedAndDestroyed)) and \
                   (not (10*row + col in self.hitNotDestroyed)):
                    self.emptyCells.append(10*row + col)


    def __findDestroyedShips(self):

        if not(self.destroyed):
            return 0

        numberCellsHit = 0
        if 5 in self.destroyed:
            numberCellsHit += 5
        if 4 in self.destroyed:
            numberCellsHit += 4
        if 3 in self.destroyed:
            numberCellsHit += 3
        if 2 in self.destroyed:
            numberCellsHit += 2
        if numberCellsHit == len(self.hitNotDestroyed):
            self.missedAndDestroyed.extend(self.hitNotDestroyed)
            self.hitNotDestroyed = []
            return 0
        
        # Find biggest first
        count = 0
        if 5 in self.destroyed:
            self.__findDestroyedShip(5)
        if 4 in self.destroyed:
            self.__findDestroyedShip(4)
        if 3 in self.destroyed:
            self.__findDestroyedShip(3)
        if 2 in self.destroyed:
            self.__findDestroyedShip(2)
        # Just to be sure...
        while(count < 3):
            if (5 in self.destroyed) and (not self.ship5IsFound):
                self.__findDestroyedShip(5)
            if (4 in self.destroyed) and (not self.ship4IsFound):
                self.__findDestroyedShip(4)
            if (3 in self.destroyed) and (not self.ship3IsFound):
                self.__findDestroyedShip(3)
            if (2 in self.destroyed) and (not self.ship2IsFound):
                self.__findDestroyedShip(2)
            count += 1


    def __findDestroyedShip(self, size):

        numberFound = 0
        neighbors = 0
        nLeft, nRight, nTop, nBottom = 0, 0, 0, 0
        for hit in self.hitNotDestroyed:
            if (1 + self.__horizNeighbors(hit, self.hitNotDestroyed) == size) or \
               (1 + self.__vertNeighbors(hit, self.hitNotDestroyed)  == size):
                numberFound += 1

        if numberFound == size:
            for hit in self.hitNotDestroyed:
                if 1 + self.__horizNeighbors(hit, self.hitNotDestroyed) == size:
                    nLeft = self.__leftNeighbors(hit, self.hitNotDestroyed)
                    nRight = self.__rightNeighbors(hit, self.hitNotDestroyed)
                    for i in range(1,nLeft+1) :
                        self.missedAndDestroyed.append(hit-10*i)
                        self.hitNotDestroyed.remove(hit-10*i)
                    for i in range(1,nRight+1) :
                        self.missedAndDestroyed.append(hit+10*i)
                        self.hitNotDestroyed.remove(hit+10*i)
                    self.missedAndDestroyed.append(hit)
                    self.hitNotDestroyed.remove(hit)
                    break
                elif 1 + self.__vertNeighbors(hit, self.hitNotDestroyed) == size:
                    nTop = self.__topNeighbors(hit, self.hitNotDestroyed)
                    nBottom = self.__bottomNeighbors(hit, self.hitNotDestroyed)
                    for i in range(1,nTop+1) :
                        self.missedAndDestroyed.append(hit-i)
                        self.hitNotDestroyed.remove(hit-i)
                    for i in range(1,nBottom+1) :
                        self.missedAndDestroyed.append(hit+i)
                        self.hitNotDestroyed.remove(hit+i)
                    self.missedAndDestroyed.append(hit)
                    self.hitNotDestroyed.remove(hit)
                    break
        else:
            destroyingMove = self.__findMoveDestroyingShip(size)
            destroyingIndex = self.intMyHits.index(destroyingMove)
            destroyedSize = size
            left, right, top, bottom = False, False, False, False
            left   = self.__checkIfDestroyedLeft(destroyingMove, destroyingIndex, destroyedSize)
            right  = self.__checkIfDestroyedRight(destroyingMove, destroyingIndex, destroyedSize)
            top    = self.__checkIfDestroyedTop(destroyingMove, destroyingIndex, destroyedSize)
            bottom = self.__checkIfDestroyedBottom(destroyingMove, destroyingIndex, destroyedSize)

            possib = 0
            if left:
                possib += 1
            if right:
                possib += 1
            if top:
                possib += 1
            if bottom:
                possib += 1
            if possib > 1:
                return 0

            self.hitNotDestroyed.remove(destroyingMove)
            self.missedAndDestroyed.append(destroyingMove)
            if (left):
                for index in range(1, destroyedSize):
                    self.hitNotDestroyed.remove(destroyingMove - 10*index)
                    self.missedAndDestroyed.append(destroyingMove - 10*index)
            if (right):
                for index in range(1, destroyedSize):
                    self.hitNotDestroyed.remove(destroyingMove + 10*index)
                    self.missedAndDestroyed.append(destroyingMove + 10*index)
            if (top):
                for index in range(1, destroyedSize):
                    self.hitNotDestroyed.remove(destroyingMove - index)
                    self.missedAndDestroyed.append(destroyingMove - index)
            if (bottom):
                for index in range(1, destroyedSize):
                    self.hitNotDestroyed.remove(destroyingMove + index)
                    self.missedAndDestroyed.append(destroyingMove + index)

        if (size == 2):
            self.ship2IsFound = True
        if (size == 3):
            self.ship3IsFound = True
        if (size == 4):
            self.ship4IsFound = True
        if (size == 5):
            self.ship5IsFound = True

    def __findMoveDestroyingShip(self, size):

        index = self.destroyed.index(size)
        currIndex = -1
        for move in self.intMyTurns:
            if (move % 10 == 4):
                currIndex += 1
            if (currIndex == index):
                return move / 10


    def __checkIfDestroyedLeft(self, destroyingMove, destroyingIndex, destroyedSize):

        leftNeighbors = 1 + self.__leftNeighbors(destroyingMove, self.hitNotDestroyed)

        if (leftNeighbors < destroyedSize):
            return False

        neighborsMoves = []
        for index in range(1, destroyedSize):
            neighborsMoves.append(destroyingMove - 10*index)

        neighborsHit = 1
        for index in range(0, destroyingIndex):
            if (self.intMyHits[index] in neighborsMoves) and \
               (self.intMyHits[index] in self.hitNotDestroyed):
                neighborsHit += 1

        return (neighborsHit == destroyedSize)


    def __checkIfDestroyedRight(self, destroyingMove, destroyingIndex, destroyedSize):

        rightNeighbors = 1 + self.__rightNeighbors(destroyingMove, self.hitNotDestroyed)

        if (rightNeighbors < destroyedSize):
            return False

        neighborsMoves = []
        for index in range(1, destroyedSize):
            neighborsMoves.append(destroyingMove + 10*index)

        neighborsHit = 1
        for index in range(0, destroyingIndex):
            if (self.intMyHits[index] in neighborsMoves) and \
               (self.intMyHits[index] in self.hitNotDestroyed):
                neighborsHit += 1

        return (neighborsHit == destroyedSize)


    def __checkIfDestroyedTop(self, destroyingMove, destroyingIndex, destroyedSize):

        topNeighbors = 1 + self.__topNeighbors(destroyingMove, self.hitNotDestroyed)

        if (topNeighbors < destroyedSize):
            return False

        neighborsMoves = []
        for index in range(1, destroyedSize):
            neighborsMoves.append(destroyingMove - index)

        neighborsHit = 1
        for index in range(0, destroyingIndex):
            if (self.intMyHits[index] in neighborsMoves) and \
               (self.intMyHits[index] in self.hitNotDestroyed):
                neighborsHit += 1

        return (neighborsHit == destroyedSize)


    def __checkIfDestroyedBottom(self, destroyingMove, destroyingIndex, destroyedSize):

        bottomNeighbors = 1 + self.__bottomNeighbors(destroyingMove, self.hitNotDestroyed)

        if (bottomNeighbors < destroyedSize):
            return False

        neighborsMoves = []
        for index in range(1, destroyedSize):
            neighborsMoves.append(destroyingMove + index)

        neighborsHit = 1
        for index in range(0, destroyingIndex):
            if (self.intMyHits[index] in neighborsMoves) and \
               (self.intMyHits[index] in self.hitNotDestroyed):
                neighborsHit += 1

        return (neighborsHit == destroyedSize)


    def __horizNeighbors(self, move, moveList):

        return self.__leftNeighbors(move, moveList) + self.__rightNeighbors(move, moveList)

    def __vertNeighbors(self, move, moveList):

        return self.__topNeighbors(move, moveList) + self.__bottomNeighbors(move, moveList)

    def __leftNeighbors(self, move, moveList):

        if (move - 10) in moveList:
           return 1 + self.__leftNeighbors(move - 10, moveList)
        return 0

    def __rightNeighbors(self, move, moveList):

        if (move + 10) in moveList:
            return 1 + self.__rightNeighbors(move + 10, moveList)
        return 0

    def __topNeighbors(self, move, moveList):

        if (move - 1) in moveList:
            return 1 + self.__topNeighbors(move - 1, moveList)
        return 0

    def __bottomNeighbors(self, move, moveList):

        if (move + 1) in moveList:
            return 1 + self.__bottomNeighbors(move + 1, moveList)
        return 0


    def __initChancesToHaveShips(self):

        for row in range(0,8):
            for col in range(0,8):
                self.chancesToHaveShips[10*row + col] = -1


    def __countPossibilities(self, move):

        possib = 0

        nLeft = self.__leftNeighbors(move, self.emptyCells)
        nRight = self.__rightNeighbors(move, self.emptyCells)
        nTop = self.__topNeighbors(move, self.emptyCells)
        nBottom = self.__bottomNeighbors(move, self.emptyCells)
        hNeighbors = nLeft + nRight
        vNeighbors = nTop + nBottom

        if not(2 in self.destroyed):
            possib += min(nLeft,1) + min(nRight,1) + min(nTop,1) + min(nBottom,1)
        if not(3 in self.destroyed):
            if hNeighbors > 1:
                possib += 1 + min(2, min(nLeft,nRight))
            if vNeighbors > 1:
                possib += 1 + min(2, min(nTop,nBottom))
        if not(4 in self.destroyed):
            if hNeighbors > 2:
                possib += 1 + min(3, min(nLeft,nRight))
            if vNeighbors > 2:
                possib += 1 + min(3, min(nTop,nBottom))
        if not(5 in self.destroyed):
            if hNeighbors > 3:
                possib += 1 + min(4, min(nLeft,nRight))
            if vNeighbors > 3:
                possib += 1 + min(4, min(nTop,nBottom))

        # There is a shot to make next to this cell
        nLeft = self.__leftNeighbors(move, self.hitNotDestroyed)
        nRight = self.__rightNeighbors(move, self.hitNotDestroyed)
        nTop = self.__topNeighbors(move, self.hitNotDestroyed)
        nBottom = self.__bottomNeighbors(move, self.hitNotDestroyed)
        hNeighbors = nLeft + nRight
        vNeighbors = nTop + nBottom
        possib += 100 * (hNeighbors * hNeighbors + vNeighbors * vNeighbors)

        return possib


    def __computeChances(self):
        
        #total = 0

        for point in self.emptyCells:
            #total += self.__countPossibilities(point)
            self.chancesToHaveShips[point] = self.__countPossibilities(point)
        #print(total)

    def __mirrorHorizontal(self, location, size, orientation):

        row = location % 10
        col = location / 10
        if (orientation == "vertical"):
            return row + 10 * (7 - col)

        # orientation == horizontal
        return row + 10 * (7 - (col + size - 1))

    def __mirrorVertical(self, location, size, orientation):

        row = location % 10
        col = location / 10
        if (orientation == "horizontal"):
            return 7 - row + 10 * col

        # orientation == vertical
        return 7 - (row + size - 1) + 10 * col

    def __getBoard(self):

        horizontal = "horizontal"
        vertical   = "vertical"
        moveBottom = random.randint(0, 1)

        
        if (moveBottom == 0):
            orientation3 = vertical
        else:
            orientation3 = horizontal
        orientation4 = horizontal
        orientation5 = horizontal

        moveTop   = random.randint(0, 1)
        moveRight = random.randint(0, 1)

        posShip2  = random.randint(1, 6)

        if (posShip2 < 4):
            location2 = (57 + 10 * max(random.randint(0, 1), moveRight)) - 7 * moveBottom * random.randint(0, 1)
            orientation2 = horizontal
        elif (posShip2 == 4):
            location2 = 75 + random.randint(0, 1)
            orientation2 = vertical
        else:
            location2 = 65
            orientation2 = horizontal

        location3 = 00 + random.randint(0, 1) * (1 - moveBottom)
        location4 = 07 - moveTop + 10 * moveRight
        location5 = 30 + moveBottom

        if (random.randint(0, 1) == 1):
            location2 = self.__mirrorHorizontal(location2, 2, orientation2)
            location3 = self.__mirrorHorizontal(location3, 3, orientation3)
            location4 = self.__mirrorHorizontal(location4, 4, orientation4)
            location5 = self.__mirrorHorizontal(location5, 5, orientation5)
        if (random.randint(0, 1) == 1):
            location2 = self.__mirrorVertical(location2, 2, orientation2)
            location3 = self.__mirrorVertical(location3, 3, orientation3)
            location4 = self.__mirrorVertical(location4, 4, orientation4)
            location5 = self.__mirrorVertical(location5, 5, orientation5)

        if (location2 < 10):
            location2 = "0" + str(location2)
        if (location3 < 10):
            location3 = "0" + str(location3)
        if (location4 < 10):
            location4 = "0" + str(location4)
        if (location5 < 10):
            location5 = "0" + str(location5)

        ship_positions = {
            2: {
                "point": str(location2),
                "orientation": orientation2
            },
            3: {
                "point": str(location3),
                "orientation": orientation3
            },
            4: {
                "point": str(location4),
                "orientation": orientation4
            },
            5: {
                "point": str(location5),
                "orientation": orientation5
            }
        }

        return ship_positions


    def __getBestMove(self):

        best_point, best_chance = None, -1
        eqPossib = []

        for point in self.chancesToHaveShips:
            if self.chancesToHaveShips[point] > best_chance:
                best_point = point
                best_chance = self.chancesToHaveShips[point]

        for point in self.chancesToHaveShips:
            if self.chancesToHaveShips[point] == best_chance:
                eqPossib.append(point)

        index = random.randint(0, len(eqPossib) - 1)

        next_move = eqPossib[index]
        if next_move < 10:
            next_move = "0" + str(next_move)

        return {
            "move": str(next_move)
        }


    def shoot(self):

        output = None
        if self.command == "init":
            output = self.__getBoard()
        elif self.command == "move":
            output = self.__getBestMove()

        print json.dumps(output)


if __name__ == "__main__":
    random.seed()
    jsonFile = json.loads(sys.argv[1])
    bot_battleship = Battleship(jsonFile)
    bot_battleship.shoot()
