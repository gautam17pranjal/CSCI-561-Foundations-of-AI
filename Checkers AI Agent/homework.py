from time import process_time

COLS = "abcdefgh"
WIN = 100000            # score for a won position (side to move has no moves)
MAN, KING = 100, 160    # material values
ADVANCE = 3             # bonus per row a man has advanced
BACK_ROW = 8            # bonus for a man still guarding its own back row
MAX_DEPTH = 20

class TimeUp(Exception):
    pass

def opponent(color):
    return "BLACK" if color == "WHITE" else "WHITE"

def kingRow(color):     # row where a man of this color gets crowned
    return 0 if color == "WHITE" else 7

def directions(color, king):
    if king:
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    if color == "WHITE":    # white moves up the board
        return [(-1, -1), (-1, 1)]
    return [(1, -1), (1, 1)]  # black moves down the board

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

# checkers board class, empty cells are None
class Board:
    def __init__(self, board, piece):
        self.board = []
        self.piece = piece  # which color you are assigned
        for i in range(8):
            row = []
            for j, val in enumerate(board[i]):
                if val in "bB":
                    row.append(Piece(i, j, "BLACK", val == "B"))
                elif val in "wW":
                    row.append(Piece(i, j, "WHITE", val == "W"))
                else:
                    row.append(None)
            self.board.append(row)

    def copy(self):     # much faster than deepcopy
        new = Board.__new__(Board)
        new.piece = self.piece
        new.board = [[None if p is None else Piece(p.row, p.col, p.color, p.isKing) for p in row] for row in self.board]
        return new

    def getPieces(self, color):
        return [p for row in self.board for p in row if p is not None and p.color == color]

    def simpleMoves(self, piece):
        moves = []
        for dr, dc in directions(piece.color, piece.isKing):
            r, c = piece.row + dr, piece.col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] is None:
                moves.append([(piece.row, piece.col), (r, c)])
        return moves

    def jumpMoves(self, piece):     # every complete jump sequence for this piece
        paths = []
        self.findJumps(piece, piece.row, piece.col, [(piece.row, piece.col)], set(), paths)
        return paths

    def findJumps(self, piece, row, col, path, captured, paths):
        extended = False
        for dr, dc in directions(piece.color, piece.isKing):
            mr, mc, lr, lc = row + dr, col + dc, row + 2*dr, col + 2*dc
            if not (0 <= lr < 8 and 0 <= lc < 8):
                continue
            mid = self.board[mr][mc]
            if mid is None or mid.color == piece.color or (mr, mc) in captured:
                continue
            land = self.board[lr][lc]
            if land is not None and land is not piece:  # the start square is free once the piece leaves it
                continue
            extended = True
            captured.add((mr, mc))
            path.append((lr, lc))
            if not piece.isKing and lr == kingRow(piece.color):
                paths.append(list(path))    # getting crowned ends the move
            else:
                self.findJumps(piece, lr, lc, path, captured, paths)
            path.pop()
            captured.discard((mr, mc))
        if not extended and len(path) > 1:  # sequence can't be extended so it is complete
            paths.append(list(path))

    def getMoves(self, color):  # returns (list of paths, isJump); jumps are mandatory
        jumps, simple = [], []
        for p in self.getPieces(color):
            jumps.extend(self.jumpMoves(p))
            if not jumps:
                simple.extend(self.simpleMoves(p))
        if jumps:
            return jumps, True
        return simple, False

    def applyMove(self, path):  # returns a new board with the move made
        new = self.copy()
        r, c = path[0]
        piece = new.board[r][c]
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            if abs(r2 - r1) == 2:   # remove the jumped over piece
                new.board[(r1 + r2)//2][(c1 + c2)//2] = None
        new.board[r][c] = None
        er, ec = path[-1]
        new.board[er][ec] = piece
        piece.movePiece(er, ec)
        if er == kingRow(piece.color):
            piece.makeKing()
        return new

    def evalFunction(self, color):  # score from the point of view of color
        mine, theirs, positional = 0, 0, 0
        myKings, enemies = [], []
        for row in self.board:
            for p in row:
                if p is None:
                    continue
                if p.isKing:
                    val, pos = KING, 0
                else:
                    advanced = 7 - p.row if p.color == "WHITE" else p.row
                    val = MAN
                    pos = advanced * ADVANCE + (BACK_ROW if advanced == 0 else 0)
                if p.color == color:
                    mine += val
                    positional += pos
                    if p.isKing:
                        myKings.append(p)
                else:
                    theirs += val
                    positional -= pos
                    enemies.append(p)
        # when ahead, trading pieces makes the lead count for more
        trade = (mine - theirs) * 20 // (mine + theirs) if mine + theirs else 0
        # when ahead, kings should close in on enemy pieces instead of waiting
        chase = 0
        if mine > theirs and enemies:
            for k in myKings:
                chase -= 2 * min(max(abs(k.row - e.row), abs(k.col - e.col)) for e in enemies)
        return mine - theirs + positional + trade + chase

    def key(self):  # board as a string, used to detect repeated positions
        return "".join("." if p is None else (p.color[0] if p.isKing else p.color[0].lower()) for row in self.board for p in row)

    def printBoard(self):
        for row in self.board:
            print("".join("." if p is None else (p.color[0].upper() if p.isKing else p.color[0].lower()) for p in row))

def miniMax(pos, depth, maxLayer, color, alpha, beta, deadline):
    # color is the agent's color, it moves on max layers and the opponent on min layers
    if process_time() > deadline:
        raise TimeUp
    toMove = color if maxLayer else opponent(color)
    moves, isJump = pos.getMoves(toMove)
    if not moves:   # side to move is blocked or has no pieces, so it loses; prefer faster wins
        return (-(WIN + depth) if maxLayer else WIN + depth), None
    if depth <= 0 and not isJump:   # keep searching forced jumps past the depth limit
        return pos.evalFunction(color), None
    resMove = None
    if maxLayer:
        bestVal = float('-inf')
        for move in moves:
            val = miniMax(pos.applyMove(move), depth-1, False, color, alpha, beta, deadline)[0]
            if val > bestVal:
                bestVal, resMove = val, move
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                break
    else:
        bestVal = float('inf')
        for move in moves:
            val = miniMax(pos.applyMove(move), depth-1, True, color, alpha, beta, deadline)[0]
            if val < bestVal:
                bestVal, resMove = val, move
            beta = min(beta, bestVal)
            if beta <= alpha:
                break
    return bestVal, resMove

def timeBudget(gType, timeLeft):    # CPU seconds to spend searching this move
    if gType == "SINGLE":
        return max(0.0, min(timeLeft * 0.5, timeLeft - 1.0))
    if timeLeft < 2:
        return 0.0
    return min(timeLeft / 30, 8.0)

def chooseMove(b, color, budget, seen=()):
    # seen holds keys of positions already reached this game; going back to one heads for a draw
    moves, isJump = b.getMoves(color)
    if len(moves) <= 1:
        return (moves[0] if moves else None), isJump
    start = process_time()
    deadline = start + budget
    best = moves[0]
    for depth in range(1, MAX_DEPTH + 1):
        # search the previous best move first so alpha-beta prunes more
        ordered = [best] + [m for m in moves if m is not best]
        alpha, depthBest = float('-inf'), None
        try:
            for move in ordered:
                child = b.applyMove(move)
                if child.key() in seen:
                    val = 0     # repeated position scores as a draw
                else:
                    # depth 1 always finishes so there is a sensible move even with no time
                    val = miniMax(child, depth-1, False, color, alpha, float('inf'),
                                  deadline if depth > 1 else float('inf'))[0]
                if val > alpha:
                    alpha, depthBest = val, move
        except TimeUp:
            break
        best = depthBest
        if alpha >= WIN or process_time() - start > budget / 3:  # forced win found, or next depth won't finish
            break
    return best, isJump

def square(pos):    # (row, col) -> name like "a1", row 0 is rank 8
    return COLS[pos[1]] + str(8 - pos[0])

def printOutputFile(path, isJump):   # printing the move to output file
    char = "J" if isJump else "E"
    with open("output.txt", "w") as f:
        for a, b in zip(path, path[1:]):
            f.write(char + " " + square(a) + " " + square(b) + "\n")

def main():
    start = process_time()
    with open("input.txt", "r") as f:
        tokens = f.read().split()
    gType, color, timeLeft = tokens[0], tokens[1], float(tokens[2])
    b = Board(tokens[3:11], color)
    seen = []
    if gType == "GAME":     # playdata.txt keeps the positions seen so far, the grader deletes it before each game
        try:
            with open("playdata.txt", "r") as f:
                seen = f.read().split()
        except FileNotFoundError:
            pass
        seen.append(b.key())
    move, isJump = chooseMove(b, color, timeBudget(gType, timeLeft), set(seen))
    if move is not None:
        printOutputFile(move, isJump)
        if gType == "GAME":
            seen.append(b.applyMove(move).key())
            with open("playdata.txt", "w") as f:
                f.write("\n".join(seen) + "\n")
    print(process_time() - start)

if __name__ == "__main__":
    main()
