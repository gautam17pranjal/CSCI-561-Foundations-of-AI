from copy import deepcopy
from time import perf_counter

# checkers piece class
class Piece:
    def __init__(self, row, col, color, king):
        self.row = row
        self.col = col
        self.color = color
        self.isKing = king
    
    def makeKing(self):
        self.isKing = True
    
    def movePiece(self, row, col):
        self.row = row
        self.col = col 

# checkers board class
class Board:
    def __init__(self, board, piece):
        self.board = []
        self.piece = piece  # which color you are assigned
        w, b, kw, kb = 0, 0, 0, 0
        for i in range(8):
            row = []
            for j, val in enumerate(board[i]):
                if(val == 'b'):
                    p = Piece(i, j, 'BLACK', False)
                    b += 1
                elif(val == 'B'):
                    p = Piece(i, j, 'BLACK', True)
                    kb += 1
                elif(val == 'w'):
                    p = Piece(i, j, 'WHITE', False)
                    w += 1
                elif(val == 'W'):
                    p = Piece(i, j, 'WHITE', True)
                    kw += 1
                else:
                    p = Piece(i, j, "None", False)
                row.append(p)
            self.board.append(row)
        self.whiteLeft, self.blackLeft = w, b
        self.whiteKing, self.blackKing = kw, kb 

    def evalFunction(self):
        # find number of w, b, wk, bk and then calculate the value. 
        eVal = 0
        for i in range(8): 
            for j in range(8):
                if(self.board[i][j] is not None): # not an empty cell   
                    if(self.board[i][j].color == "WHITE"):
                        if(self.board[i][j].isKing):
                            # left up and down jump
                            t = False
                            if(j-2>=0 and i-2>=0):
                                if(self.board[i-1][j-1] is not None and self.board[i-1][j-1].color=="BLACK" and self.board[i-2][j-2] is None):
                                    eVal += 5
                                    t = True
                            if(j-2>=0 and i+2<8):
                                if(self.board[i+1][j-1] is not None and self.board[i+1][j-1].color=="BLACK" and self.board[i+2][j-2] is None):
                                    eVal += 5
                                    t = True
                            # right up and down jump
                            if(i-2>=0 and j+2<8):
                                if(self.board[i-1][j+1] is not None and self.board[i-1][j+1].color=="BLACK" and self.board[i-2][j+2] is None):
                                    eVal += 5
                                    t = True
                            if(i+2<8 and j+2<8):
                                if(self.board[i+1][j+1] is not None and self.board[i+1][j+1].color=="BLACK" and self.board[i+2][j+2] is None):
                                    eVal += 5
                                    t = True
                            if(not t):
                                eVal += 3
                        else:
                            # jump condition non king can jump up only -> white
                            t = False
                            if(i-2>=0 and j-2>=0):
                                if(self.board[i-1][j-1] is not None and self.board[i-1][j-1].color=="BLACK" and self.board[i-2][j-2] is None):
                                    eVal += 2
                                    t = True
                            if(i-2>=0 and j+2<8):
                                if(self.board[i-1][j+1] is not None and self.board[i-1][j+1].color=="BLACK" and self.board[i-2][j+2] is None):
                                    eVal += 2
                                    t = True
                            # cannot jump 
                            if(not t):
                                eVal += 1
                    if(self.board[i][j].color == "BLACK"):
                        if(self.board[i][j].isKing):    # jump condition king
                            # left up and down jump
                            t = False
                            if(j-2>=0 and i-2>=0):
                                if(self.board[i-1][j-1] is not None and self.board[i-1][j-1].color=="WHITE" and self.board[i-2][j-2] is None):
                                    eVal += 5
                                    t = True
                            if(j-2>=0 and i+2<8):
                                if(self.board[i+1][j-1] is not None and self.board[i+1][j-1].color=="WHITE" and self.board[i+2][j-2] is None):
                                    eVal += 5
                                    t = True
                            # right up and down jump
                            if(i-2>=0 and j+2<8):
                                if(self.board[i-1][j+1] is not None and self.board[i-1][j+1].color=="WHITE" and self.board[i-2][j+2] is None):
                                    eVal += 5
                                    t = True
                            if(i+2<8 and j+2<8):
                                if(self.board[i+1][j+1] is not None and self.board[i+1][j+1].color=="WHITE" and self.board[i+2][j+2] is None):
                                    eVal += 5
                                    t = True
                            if(not t):
                                eVal += 3
                        else:
                            # jump condition non king can jump down only -> black
                            t = False
                            if(i+2<8 and j-2>=0):
                                if(self.board[i+1][j-1] is not None and self.board[i+1][j-1].color=="WHITE" and self.board[i+2][j-2] is None):
                                    eVal += 2
                                    t = True
                            if(i+2<8 and j+2<8):
                                if(self.board[i+1][j+1] is not None and self.board[i+1][j+1].color=="WHITE" and self.board[i+2][j+2] is None):
                                    eVal += 2
                                    t = True
                            # cannot jump 
                            if(not t):
                                eVal += 1
        return eVal
    
    def piece2(self, row, col):     # returns the position of piece helful in minimax-> deepcopy issue
        return self.board[row][col]
    
    def getColor(self, row, col):
        return self.board[row][col].color
    
    def getPieceColorWise(self):
        w, b = 0, 0
        for i in range(8):
            for j in range(8):
                if(self.board[i][j].color == "WHITE"):
                    w += 1
                if(self.board[i][j].color == "BLACK"):
                    b += 1
        return (w, b)

    def getPieces(self, color):     # for a move what are all the valid pieces available of one color .
        bp = []
        for i in self.board:
            for p in i:
                if(p is not None and p.color != None and p.color == color):
                    bp.append(p)
        return bp

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.movePiece(row, col)
        # check king
        if(row == 7 or row == 0):
            piece.makeKing()
            if(piece.color == "WHITE"):
                self.whiteKing += 1
            elif(piece.color == "BLACK"):
                self.blackKing += 1
            elif(piece.color == "None"):
                None

    def validMoves(self, piece):
        r = piece.row
        moveLeft, moveRight = piece.col-1, piece.col+1
        move = {}
        if(piece.color == "WHITE"):
            if(not piece.isKing):
                move.update(self.goLeft(r-1, -1, -1, piece.color, moveLeft))
                move.update(self.goRight(r-1, -1, -1, piece.color, moveRight))
            else:   # white king piece
                move.update(self.goLeft(r-1, -1, -1, piece.color, moveLeft))
                move.update(self.goRight(r-1, -1, -1, piece.color, moveRight))
                move.update(self.goLeft(r+1, 8, 1, piece.color, moveLeft))
                move.update(self.goRight(r+1, 8, 1, piece.color, moveRight))
        elif(piece.color == "BLACK"):
            if(not piece.isKing):
                move.update(self.goLeft(r+1, 8, 1, piece.color, moveLeft))
                move.update(self.goRight(r+1, 8, 1, piece.color, moveRight))
            else:   # black king piece
                # up movement
                move.update(self.goLeft(r-1, -1, -1, piece.color, moveLeft))
                move.update(self.goRight(r-1, -1, -1, piece.color, moveRight))
                # down movement
                move.update(self.goLeft(r+1, 8, 1, piece.color, moveLeft))
                move.update(self.goRight(r+1, 8, 1, piece.color, moveRight))
        return move
    
    # white piece going up and black piece going down--- check for left side and right side 
    def goLeft(self, start, stop, inc, color, leftCol, jumped = []):
        moves, nxt = {}, []
        for i in range(start, stop, inc):
            if(leftCol < 0 or leftCol > 7):    # goes out of board
                break
            curr = self.board[i][leftCol]
            if(curr.color == "None"):
                if(jumped and not nxt):
                    break
                elif jumped:
                    moves[(i,leftCol)] = nxt+jumped
                else:   # we can jump over
                    moves[(i, leftCol)] = nxt
                if(nxt):   # found 1 jump and then check for new jumps
                    tstop = 0
                    if(inc == -1):
                        tstop = -1
                    else:
                        tstop = 8
                    moves.update(self.goLeft(i+inc, tstop, inc, color, leftCol-1, jumped=nxt))
                    moves.update(self.goRight(i+inc, tstop, inc, color, leftCol+1, jumped=nxt))
                break
            elif(curr.color == color):      # the next cell is blocked by the same color
                break
            else:           # the next cell is blocked but of different color
                nxt = [(curr.row, curr.col)]
                if(leftCol-1 >=0 and i+1<8 and i-1>=0):
                    if(inc == 1 and self.board[i+1][leftCol-1].color != "None") or (inc == -1 and self.board[i-1][leftCol-1].color != "None"):
                        break
            leftCol -= 1
        return moves

    def goRight(self, start, stop, inc, color, rightCol, jumped = []):
        moves, nxt = {}, []
        for i in range(start, stop, inc):
            if(rightCol < 0 or rightCol > 7):   # goes out of board
                break
            curr = self.board[i][rightCol]
            if(curr.color == "None"):
                if(jumped and not nxt):
                    break
                elif jumped:
                    moves[(i,rightCol)] = nxt + jumped
                else:
                    moves[(i, rightCol)] = nxt
                if(nxt):   # found 1 jump and then check for new jumps
                    tstop = 0
                    if(inc == -1):
                        tstop = -1
                    else:
                        tstop = 8
                    moves.update(self.goLeft(i+inc, tstop, inc, color, rightCol-1, jumped=nxt))
                    moves.update(self.goRight(i+inc, tstop, inc, color, rightCol+1, jumped=nxt))
                break
            # the next cell is blocked by the same color
            elif(curr.color == color):
                break
            # the next cell is empty
            else:
                nxt = [(curr.row, curr.col)]
                if(rightCol+1 <8 and i+1<8 and i-1>=0):
                    if(inc == 1 and self.board[i+1][rightCol+1].color != "None") or (inc == -1 and self.board[i-1][rightCol+1].color != "None"):
                        break
            rightCol += 1
        return moves

    def removePiece(self, pieces):  # remove the jumped over pieces from the board
        for p in pieces:
            if(p is not None):      # decrement the counter for whiteleft and blackleft
                if self.board[p[0]][p[1]].color == "WHITE":
                    self.whiteLeft -= 1
                else:
                    self.blackLeft -= 1
            self.board[p[0]][p[1]].color = "None"    

    def printBoard(self):
        for i in range(8): 
            for j in range(8):
                if(self.board[i][j] is not None): 
                    print(self.board[i][j].color, end = " ")
                else:
                    print(None, end = " ")
            print(" ")
    
    def endGame(self):
        if(self.whiteLeft <= 0):
            return "BLACK"
        elif(self.blackLeft <= 0):
            return "WHITE"
        return None

def miniMax(pos, depth, maxLayer, color, alpha, beta):
    if(depth == 0 or pos.endGame() != None):      # depth level reached or game finished before last level 
        return(pos.evalFunction(), pos)
    # if the layer is for maximizing
    if(maxLayer):
        resMove = None
        bestVal = float('-inf')
        for move in getMoves(pos, color):   # move is of the format (board, piece) i.e for piece 'p' the move made to get the board
            if(color == "WHITE"):
                color = "BLACK"
            else:
                color = "WHITE"
            eval = miniMax(move[0], depth-1, False, color, alpha, beta)[0]
            bestVal = max(bestVal, eval)
            alpha = max(alpha, bestVal)
            if(bestVal == eval):
                resMove = move
            if(alpha == bestVal):
                resMove = move     # store the new board pos and the piece that we moved to [pos, piece]
            if(beta <= alpha):
                break
        return(alpha, resMove)
    else:           # if the layer is for minimizing
        resMove = None
        bestVal = float('inf')
        for move in getMoves(pos, color):
            if(color == "WHITE"):
                color = "BLACK"
            else:
                color = "WHITE"
            eval = miniMax(move[0], depth-1, True, color, alpha, beta)[0]
            bestVal = min(bestVal, eval)
            beta = min(beta, bestVal)
            if(bestVal == eval):
                resMove = move
            if(beta == bestVal):
                resMove = move     # store the new board pos and the piece that we moved [pos, piece]
            if(beta <= alpha):
                break
        return(beta, resMove)

def makeTempMove(p, pos, move, jumped):
    pos.move(p, move[0], move[1])
    if jumped:
        pos.removePiece(jumped)
    return pos

def getMoves(pos, color):       # prioritize jump moves first
    jumpPiece, freePiece, moves = [], [], []
    for p in pos.getPieces(color):
        valMove = pos.validMoves(p)
        isJump, route = check(p, valMove)
        if(isJump):
            jumpPiece.append((p, valMove))
        else:
            freePiece.append((p, valMove))
    if(len(jumpPiece) != 0):
        for data in jumpPiece:      # data == [p, valMove]
            for move, jumped in data[1].items():
                if(jumped):     # discard the non-jump moves in tree
                    currPos = deepcopy(pos)
                    currPiece = currPos.piece2(data[0].row, data[0].col)
                    newPos = makeTempMove(currPiece, currPos, move, jumped)
                    moves.append([newPos, currPiece])
    else:
        for data in freePiece:
            for move, jumped in data[1].items():
                currPos = deepcopy(pos)
                currPiece = currPos.piece2(data[0].row, data[0].col)
                newPos = makeTempMove(currPiece, currPos, move, jumped)
                moves.append([newPos, currPiece])
    return moves

def compare(oldBoard, newBoard, color):     # color is the piece color our agent moves
    pieceOld, pieceNew = [], []
    wOld, bOld, wNew, bNew = 0, 0, 0, 0
    charType = ""
    for i in range(8):
        for j in range(8):
            oldColor = oldBoard.getColor(i, j)
            newColor = newBoard.getColor(i, j)
            if(oldColor == "WHITE"):
                wOld += 1
            if(oldColor == "BLACK"):
                bOld += 1
            if(newColor == "WHITE"):
                wNew += 1
            if(newColor == "BLACK"):
                bNew += 1
            if(oldColor == color and newColor != color):    # initial position of the piece
                pieceOld.append((i,j))
            if(oldColor != color and newColor == color):    # final position of the piece
                pieceNew.append((i,j))
    if(color == "WHITE"):
        if(bNew < bOld):    # this means the white piece that agent moved was jumped over black pieces
            charType = "J"
        else:
            charType = "E"
    elif(color == "BLACK"):
        if(wNew < wOld):
            charType = "J"
        else:
            charType = "E"
    return (charType, pieceOld, pieceNew)            

def calculateDepth(board, color, time):
    depth = 3 
    w, b = board.getPieceColorWise()
    if(w == b):
        diff = time-3
        if(diff > 0):
            if(diff > 2):
                depth = 5
            elif(diff > 1.5 and diff < 2):
                depth = 4
            else:
                depth = 3
        else:
            if(time > 1.5 and time < 3):
                depth = 4
            else:       
                depth = 3
        return depth
    diff = time-10    
    if(diff > 0):
        if(diff > 10):
            depth = 7
        elif(diff > 5 and diff < 10):
            depth = 6
        elif(diff > 3 and diff < 5):
            depth = 5
        elif(diff > 1.5 and diff < 3):
            depth = 4
        else:
            depth = 3
    else:
        if(time > 5 and time < 10):   
            depth = 6
        elif(time > 3 and time < 5):
            depth = 5
        elif(time > 1.5 and time < 3):
            depth = 4
        else:       
            depth = 3     
    return depth

def miniMaxUtil(b, time, color):  
    time = float(time)
    depth = calculateDepth(b, color, time)
    # depth = 6
    print(depth)
    value, newBoard = miniMax(b, depth, True, color, float('-inf'), float('inf'))
    charType, pieceOld, pieceNew = compare(b, newBoard[0], color)
    if(charType == "E"):
        printOutputFile("E", pieceOld+pieceNew)
    else:
        p = b.piece2(pieceOld[0][0], pieceOld[0][1])
        valMove = b.validMoves(p)
        isJump, route = check(p, valMove)
        printOutputFile("J", route)

# single game mode
def singleMove(board, color):
    t = False
    for p in board.getPieces(color):
        valMove = board.validMoves(p)
        isJump, route = check(p, valMove)
        if(isJump):
            t = True
            break
    return (t, route)

def check(p, valMove):  # find the route of the piece taken 
    isJump = False
    route = [(p.row, p.col)]
    temp = []
    if(len(valMove) != 0):  # some move exists for that piece
        for val in valMove:
            temp = val
            if(len(valMove[val]) != 0):
                isJump = True
                break
        if(isJump):     # find route
            for val in valMove:
                if(len(valMove[val]) != 0):
                    route.append(val)
        if(not isJump):
            route.append(temp)
        return (isJump, route)
    else:
        return(False, None)

def printOutputFile(char, route):   # printing the move to output file
    naming = {
        "row": {
            0: '8',
            1: '7',
            2: '6',
            3: '5',
            4: '4',
            5: '3',
            6: '2',
            7: '1'
        }, 
        "col": {
            0: 'a',
            1: 'b',
            2: 'c',
            3: 'd',
            4: 'e',
            5: 'f',
            6: 'g',
            7: 'h'
        }
    }
    f = open("TestCases/output1.txt", "w")
    for i, val in enumerate(route):
        if(i+1<len(route)):
            line = char + " " + naming["col"][route[i][1]]+naming["row"][route[i][0]] + " " + naming["col"][route[i+1][1]]+naming["row"][route[i+1][0]]
            f.write(line)
        f.write('\n')
    f.close()

start = perf_counter()
# reading the input file
f = open("TestCases/input1.txt", "r")
gType = f.readline().strip().split("\n")[0] 
# my piece color
color = f.readline().strip().split("\n")[0]
# time depending upon single or game mode
time = f.readline().strip().split("\n")[0]
board = []
for i in range(8):
    temp = f.readline().strip().split("\n")[0]
    board.append(temp)
f.close()
b = Board(board, color)
if(gType == "SINGLE"):
    isJump, route = singleMove(b, color)
    if(isJump):
        printOutputFile("J", route)
    else:
        printOutputFile("E", route)
elif(gType == "GAME"):
    miniMaxUtil(b, time, color)
end = perf_counter()-start
print(end)