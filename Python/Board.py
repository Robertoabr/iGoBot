#!/usr/bin/env python

#     iGoBot - a GO game playing robot
#
#     ##############################
#     # GO stone board coordinates #
#     ##############################
#
#     Project website: http://www.springwald.de/hi/igobot
#
#     Licensed under MIT License (MIT)
#
#     Copyright (c) 2018 Daniel Springwald | daniel@springwald.de
#
#     Permission is hereby granted, free of charge, to any person obtaining
#     a copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to permit
#     persons to whom the Software is furnished to do so, subject to
#     the following conditions:
#
#     The above copyright notice and this permission notice shall be
#     included in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#     FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#     THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#     LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#     DEALINGS IN THE SOFTWARE.


class Board():

	_released					= False
	
	Empty						= 0;
	Black						= 1;
	White						= 2;
	
	_boardSize					= 0; # 9, 13, 19
	_fields						= [];
	
	# Stepper motor positions
	_13x13_xMin						= 735; 
	_13x13_xMax						= 3350;
	_13x13_yMin						= 100; 
	_13x13_yMax						= 2890;
	
	_9x9_xMin						= 1120; 
	_9x9_xMax						= 2940;
	_9x9_yMin						= 560; 
	_9x9_yMax						= 2400;
	
	StepperMinX						= 0;
	StepperMaxX 					= 0;
	StepperMinY						= 0;
	StepperMaxY						= 0;
	
	def __init__(self, boardSize):
		self._boardSize = boardSize;
		
		if (boardSize == 13):
			#print("Board: size " , boardSize, "x", boardSize);
			self.StepperMinX = self._13x13_xMin;
			self.StepperMaxX = self._13x13_xMax
			self.StepperMinY = self._13x13_yMin;
			self.StepperMaxY = self._13x13_yMax;
		else:
			if (boardSize == 9):
				#print("Board: size " , boardSize, "x", boardSize);
				self.StepperMinX = self._9x9_xMin;
				self.StepperMaxX = self._9x9_xMax
				self.StepperMinY = self._9x9_yMin;
				self.StepperMaxY = self._9x9_yMax;
			else:
				throw ("unknown board size " , boardSize, "x", boardSize);
		
		# init board dimensions with 0 values (0=empty, 1=black, 2= white)
		self._fields =  [[0 for i in range(boardSize)] for j in range(boardSize)]
		
	@staticmethod
	def FromStones(boardSize, blackStones, whiteStones):
	# create a new board and fill it with the given black and white stones
		board = Board(boardSize)
		if (blackStones != None and len(blackStones) > 0 and blackStones[0] != ''):
			for black in Board.EnsureXyNotation(blackStones):
				board.SetField(black[0],black[1],Board.Black);
		if (whiteStones != None and len(whiteStones) > 0 and whiteStones[0] != ''):
			for white in Board.EnsureXyNotation(whiteStones):
				board.SetField(white[0],white[1],Board.White);
		return board;
	
	@staticmethod
	def Differences(board1, board2):
	# find all coordinates, where the second board is other 
		if (board1 == None): throw ("board1 == None");
		if (board2 == None): throw ("board2 == None");
		if (board1._boardSize != board2._boardSize): throw ("different board sizes: " , board1._boardSize, " vs. ", board2._boardSize);
		result = [];
		for x in range(0, board1._boardSize):
			for y in range(0, board1._boardSize):
				if (board1.GetField(x,y) != board2.GetField(x,y)):
					result.extend([[x,y]])
		return result;
		
	def RemovedStones(board1, board2):
	# find all coordinates, where the stones from board1 are not on board2
		if (board1 == None): throw ("board1 == None");
		if (board2 == None): throw ("board2 == None");
		if (board1._boardSize != board2._boardSize): throw ("different board sizes: " , board1._boardSize, " vs. ", board2._boardSize);
		result = [];
		for x in range(0, board1._boardSize):
			for y in range(0, board1._boardSize):
				if (board1.GetField(x,y) != Board.Empty):
					if (board2.GetField(x,y) == Board.Empty):
						result.extend([[x,y]])
		return result;

	@staticmethod
	def EnsureXyNotation(stones):
	#ensures that this is a list of [[x,y],[x,y]] and not like ["A1","G2]
		result = [];
		for stone in stones:
			#print(">>>1>>>", stone);
			if (isinstance(stone, str) and stone !=''):
				#print(">>>2>>>", Board.AzToXy(stone));
				result.extend([Board.AzToXy(stone)])
			else:
				#print(">>>3>>>", stones);
				return stones; # already [x,y] format
		return result;

	@staticmethod
	def XyToAz(x,y):
	# converts x=1,y=2 to A1
		if (x > 7):
			x=x+1; # i is not defined, jump to j
		return chr(65+x)+str(y+1);

	@staticmethod
	def AzToXy(azNotation):
	# converts A1 to [0,0]
		if (len(azNotation) != 2 and len(azNotation) != 3):
			print ("board.AzToXy for '" + azNotation + "' is not exact 2-3 chars long");
			return None;
		x = ord(azNotation[0])-65;
		if (x > 7):
			 x=x-1; # i is not defined, jump to h
		y = int(azNotation[1:])-1;
		return [x,y]
		
	def Print(self):
	# draw the board to console
		for y in range(0, self._boardSize):
			line = "";
			for x in range(0, self._boardSize):
				stone = self.GetField(x,y);
				if (stone==0):
					line = line + "."
				elif (stone==Board.Black):
					line = line + "*";
				elif (stone==Board.White):
					line = line + "O";
			print(line);

	def GetField(self,x,y):
		return self._fields[x][y];
		
	def SetField(self,x,y, value):
		self._fields[x][y] = value;
		
	def GetNewStones(self, detectedStones, color=Black):
	# what are the new black/whites stones in the list, not still on the board?
		newStones = [];
		for stone in detectedStones:
			if (self.GetField(stone[0],stone[1]) != color):
				newStones.extend([[stone[0],stone[1]]])
		return newStones;

	def GetStepperXPos(self, fieldX):
		return self.StepperMinX + int(fieldX * 1.0 * ((self.StepperMaxX-self.StepperMinX) / (self._boardSize-1.0)));
		
	def GetStepperYPos(self, fieldY):
		return self.StepperMinY + int(fieldY * 1.0 * ((self.StepperMaxY-self.StepperMinY) / (self._boardSize-1.0)));
		
if __name__ == '__main__':
	
	board  = Board(13)
	print (board._fields)
	print (Board.AzToXy("A1"))
	board.SetField(0,0,board.Black);
	board.SetField(12,12,board.Black);
	print(board.GetField(0,0));
	print(board.GetField(0,0) == board.Black);
	
	for x in range(0,13):
		f = board.XyToAz(x,x);
		print([x,x],f, Board.AzToXy(f));
		
	board2 = Board.FromStones(boardSize=13, blackStones=[[0,0],[1,1]], whiteStones=[[2,0],[2,1]]);
	board2.Print();
	print(Board.Differences(board,board2));
	print(Board.RemovedStones(board,board2));
	
	
