#!/bin/env python2.7

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

		# Lists that are used to compute next move
		# List of previous moves
        self.intMoves = [int(x) for x in self.moves]
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

        # Find biggest first
        if 5 in self.destroyed:
            self.__findDestroyedShip(5)
        if 4 in self.destroyed:
            self.__findDestroyedShip(4)
        if 3 in self.destroyed:
            self.__findDestroyedShip(3)
        if 2 in self.destroyed:
            self.__findDestroyedShip(2)


    def __findDestroyedShip(self, size):

        numberFound = 0
        neighbors = 0
        nLeft, nRight, nTop, nBottom = 0, 0, 0, 0
        for hit in self.hitNotDestroyed:
            if 1 + self.__horizNeighbors(hit, self.hitNotDestroyed) == size:
                numberFound += 1
            elif 1 + self.__vertNeighbors(hit, self.hitNotDestroyed) == size:
                numberFound += 1

        if numberFound != size:
            return 0

        for hit in self.hitNotDestroyed:
            if 1 + self.__horizNeighbors(hit, self.hitNotDestroyed) == size:
                nLeft = self.__leftNeighbors(hit, self.hitNotDestroyed)
                nRight = self.__rightNeighbors(hit, self.hitNotDestroyed)
                for i in range(1,nLeft+1) :
                    self.missedAndDestroyed.append(hit-i)
                    self.hitNotDestroyed.remove(hit-i)
                for i in range(1,nRight+1) :
                    self.missedAndDestroyed.append(hit+i)
                    self.hitNotDestroyed.remove(hit+i)
                self.missedAndDestroyed.append(hit)
                self.hitNotDestroyed.remove(hit)
                break
            elif 1 + self.__vertNeighbors(hit, self.hitNotDestroyed) == size:
                nTop = self.__topNeighbors(hit, self.hitNotDestroyed)
                nBottom = self.__bottomNeighbors(hit, self.hitNotDestroyed)
                for i in range(1,nTop+1) :
                    self.missedAndDestroyed.append(hit-10*i)
                    self.hitNotDestroyed.remove(hit-10*i)
                for i in range(1,nBottom+1) :
                    self.missedAndDestroyed.append(hit+10*i)
                    self.hitNotDestroyed.remove(hit+10*i)
                self.missedAndDestroyed.append(hit)
                self.hitNotDestroyed.remove(hit)
                break


    def __horizNeighbors(self, move, moveList):

        return self.__leftNeighbors(move, moveList) + self.__rightNeighbors(move, moveList)

    def __vertNeighbors(self, move, moveList):

        return self.__topNeighbors(move, moveList) + self.__bottomNeighbors(move, moveList)

    def __leftNeighbors(self, move, moveList):

        if (move - 1) in moveList:
           return 1 + self.__leftNeighbors(move - 1, moveList)
        return 0

    def __rightNeighbors(self, move, moveList):

        if (move + 1) in moveList:
            return 1 + self.__rightNeighbors(move + 1, moveList)
        return 0

    def __topNeighbors(self, move, moveList):

        if (move - 10) in moveList:
            return 1 + self.__topNeighbors(move - 10, moveList)
        return 0

    def __bottomNeighbors(self, move, moveList):

        if (move + 10) in moveList:
            return 1 + self.__bottomNeighbors(move + 10, moveList)
        return 0


    def __countPossibilities(self, move):

        possib = 1

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

        possib += 100 * (hNeighbors + vNeighbors)
        return possib


    def __computeChances(self):
        
        for point in self.emptyCells:
            self.chancesToHaveShips[point] = self.__countPossibilities(point)


    def __initChancesToHaveShips(self):

        for row in range(0,8):
            for col in range(0,8):
                self.chancesToHaveShips[10*row + col] = -1


    def __getBoard(self):

        ship_positions = {
            2: {
                "point": "67",
                "orientation": "horizontal"
            },
            3: {
                "point": "04",
                "orientation": "vertical"
            },
            4: {
                "point": "07",
                "orientation": "horizontal"
            },
            5: {
                "point": "30",
                "orientation": "horizontal"
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
    jsonFile = json.loads(sys.argv[1])
    bot_battleship = Battleship(jsonFile)
    bot_battleship.shoot()
