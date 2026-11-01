"""Test harness for homework.py.

Plays full games through the same input.txt / output.txt protocol the grader uses,
and checks every move against a rules engine written independently of homework.py.

  python3 arena.py                                   # agent vs random, 4 games
  python3 arena.py --opponent minimax:4 --games 6    # agent vs plain minimax (like the TA reference)
  python3 arena.py --agent2 other.py                 # agent vs another homework.py
  python3 arena.py --examples                        # single-move examples from the assignment PDF
"""
import argparse
import os
import random
import resource
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
START = [
    ".b.b.b.b",
    "b.b.b.b.",
    ".b.b.b.b",
    "........",
    "........",
    "w.w.w.w.",
    ".w.w.w.w",
    "w.w.w.w.",
]

# ---------- independent rules engine (grid of chars) ----------

def owner(ch):
    return "BLACK" if ch in "bB" else "WHITE" if ch in "wW" else None

def steps(ch):
    if ch in "BW":
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return [(1, -1), (1, 1)] if ch == "b" else [(-1, -1), (-1, 1)]

def crowned(ch, row):
    return (ch == "b" and row == 7) or (ch == "w" and row == 0)

def legal_moves(grid, color):
    """Returns (set of paths, is_jump). A path is a tuple of (row, col) squares."""
    jumps, simple = set(), set()
    for r in range(8):
        for c in range(8):
            ch = grid[r][c]
            if owner(ch) != color:
                continue
            stack = [((r, c), ((r, c),), frozenset())]
            while stack:
                (cr, cc), path, taken = stack.pop()
                grew = False
                for dr, dc in steps(ch):
                    over, land = (cr + dr, cc + dc), (cr + 2 * dr, cc + 2 * dc)
                    if not (0 <= land[0] < 8 and 0 <= land[1] < 8):
                        continue
                    victim = grid[over[0]][over[1]]
                    if owner(victim) not in (None, color) and over not in taken and \
                            (grid[land[0]][land[1]] == "." or land == (r, c)):
                        grew = True
                        if crowned(ch, land[0]):
                            jumps.add(path + (land,))
                        else:
                            stack.append((land, path + (land,), taken | {over}))
                if not grew and len(path) > 1:
                    jumps.add(path)
            for dr, dc in steps(ch):
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8 and grid[nr][nc] == ".":
                    simple.add(((r, c), (nr, nc)))
    return (jumps, True) if jumps else (simple, False)

def play(grid, path):
    """Returns (new grid, whether a piece was captured or crowned)."""
    g = [list(row) for row in grid]
    (r, c), (er, ec) = path[0], path[-1]
    ch = g[r][c]
    changed = False
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        if abs(r2 - r1) == 2:
            g[(r1 + r2) // 2][(c1 + c2) // 2] = "."
            changed = True
    g[r][c] = "."
    if crowned(ch, er):
        ch = ch.upper()
        changed = True
    g[er][ec] = ch
    return ["".join(row) for row in g], changed

def name(sq):
    return "abcdefgh"[sq[1]] + str(8 - sq[0])

def parse_square(s):
    return (8 - int(s[1]), "abcdefgh".index(s[0]))

def parse_output(text):
    """Turns output.txt into (path, kind) or raises ValueError."""
    lines = [l for l in text.split("\n") if l.strip()]
    if not lines:
        raise ValueError("empty output.txt")
    path, kinds = [], set()
    for line in lines:
        parts = line.split(" ")
        if len(parts) != 3 or parts[0] not in ("E", "J") or len(parts[1]) != 2 or len(parts[2]) != 2:
            raise ValueError("badly formatted line %r" % line)
        a, b = parse_square(parts[1]), parse_square(parts[2])
        if path and path[-1] != a:
            raise ValueError("jump chain is not continuous at %r" % line)
        if not path:
            path.append(a)
        path.append(b)
        kinds.add(parts[0])
    if len(kinds) > 1 or (kinds == {"E"} and len(lines) > 1):
        raise ValueError("mixed or repeated E moves")
    return tuple(path), kinds.pop()

# ---------- players ----------

class ProgramPlayer:
    """Runs a homework.py in its own temp dir, exactly like the grader would."""
    def __init__(self, script, label):
        self.script, self.label = os.path.abspath(script), label
        self.dir = tempfile.mkdtemp(prefix="checkers_")

    def new_game(self):     # the grader deletes playdata.txt before each game
        data = os.path.join(self.dir, "playdata.txt")
        if os.path.exists(data):
            os.remove(data)

    def move(self, grid, color, time_left, mode="GAME"):
        out = os.path.join(self.dir, "output.txt")
        if os.path.exists(out):
            os.remove(out)
        with open(os.path.join(self.dir, "input.txt"), "w") as f:
            f.write("%s\n%s\n%.2f\n%s\n" % (mode, color, time_left, "\n".join(grid)))
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        try:
            subprocess.run([sys.executable, self.script], cwd=self.dir, stdout=subprocess.DEVNULL,
                           stderr=subprocess.PIPE, timeout=time_left + 5, check=True)
        except subprocess.TimeoutExpired:
            return None, time_left + 5, "timed out"
        except subprocess.CalledProcessError as e:
            return None, 0.0, "crashed: " + e.stderr.decode().strip().splitlines()[-1]
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        used = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
        if not os.path.exists(out):
            return None, used, "wrote no output.txt"
        with open(out) as f:
            return f.read(), used, None

class RandomPlayer:
    def __init__(self, seed):
        self.label, self.rng = "random", random.Random(seed)

    def move(self, grid, color, time_left, mode="GAME"):
        moves, jump = legal_moves(grid, color)
        return format_move(self.rng.choice(sorted(moves)), jump), 0.0, None

class MinimaxPlayer:
    """Plain fixed-depth minimax on material, no alpha-beta: similar to the TA reference agent.
    Ties are broken at random (seeded) so repeated games differ."""
    def __init__(self, depth, seed):
        self.label, self.depth, self.rng = "minimax:%d" % depth, depth, random.Random(seed)

    def score(self, grid, color):
        s = 0
        for row in grid:
            for ch in row:
                if ch != ".":
                    v = 3 if ch in "BW" else 2
                    s += v if owner(ch) == color else -v
        return s

    def search(self, grid, color, to_move, depth):
        moves, _ = legal_moves(grid, to_move)
        if not moves:
            return -1000 if to_move == color else 1000
        if depth == 0:
            return self.score(grid, color)
        other = "BLACK" if to_move == "WHITE" else "WHITE"
        vals = [self.search(play(grid, m)[0], color, other, depth - 1) for m in moves]
        return max(vals) if to_move == color else min(vals)

    def move(self, grid, color, time_left, mode="GAME"):
        moves, jump = legal_moves(grid, color)
        other = "BLACK" if color == "WHITE" else "WHITE"
        moves = sorted(moves)
        self.rng.shuffle(moves)
        best = max(moves, key=lambda m: self.search(play(grid, m)[0], color, other, self.depth - 1))
        return format_move(best, jump), 0.0, None

def format_move(path, jump):
    return "".join("%s %s %s\n" % ("J" if jump else "E", name(a), name(b)) for a, b in zip(path, path[1:]))

def make_player(spec, seed):
    if spec == "random":
        return RandomPlayer(seed)
    if spec.startswith("minimax:"):
        return MinimaxPlayer(int(spec.split(":")[1]), seed)
    return ProgramPlayer(spec, os.path.basename(spec))

# ---------- game loop ----------

def check_move(grid, color, text):
    """Returns (path, error)."""
    try:
        path, kind = parse_output(text)
    except ValueError as e:
        return None, str(e)
    moves, jump = legal_moves(grid, color)
    if path not in moves or (kind == "J") != jump:
        return None, "illegal move %s (legal: %s)" % (
            " ".join(map(name, path)), ", ".join(" ".join(map(name, m)) for m in sorted(moves)))
    return path, None

def play_game(black, white, total_time, verbose=False, max_turns=400):
    players = {"BLACK": black, "WHITE": white}
    for p in (black, white):
        if hasattr(p, "new_game"):
            p.new_game()
    clock = {"BLACK": total_time, "WHITE": total_time}
    grid, color = START, "BLACK"
    seen, quiet = {}, 0
    for turn in range(max_turns):
        moves, _ = legal_moves(grid, color)
        other = "BLACK" if color == "WHITE" else "WHITE"
        if not moves:
            return other, "%s has no moves" % color, turn, clock
        text, used, err = players[color].move(grid, color, clock[color])
        clock[color] -= used
        if err is None and clock[color] <= 0:
            err = "ran out of time"
        if err is None:
            path, err = check_move(grid, color, text)
        if err:
            return other, "%s (%s) %s" % (color, players[color].label, err), turn, clock
        grid, changed = play(grid, path)
        if verbose:
            print("%3d %s %-28s %6.2fs left" % (turn + 1, color[0], " ".join(map(name, path)), clock[color]))
        quiet = 0 if changed else quiet + 1
        seen[tuple(grid)] = seen.get(tuple(grid), 0) + 1
        if quiet >= 50:
            return None, "draw: 50 turns without capture or crowning", turn + 1, clock
        if seen[tuple(grid)] >= 3:
            return None, "draw: position repeated 3 times", turn + 1, clock
        color = other
    return None, "draw: turn limit reached", max_turns, clock

# ---------- single-move examples from the assignment ----------

EXAMPLES = [
    ("WHITE", 100.0, [".b.b.b.b", "b.b.b.b.", ".b...b.b", "....b...", "........", "w.w.w.w.", ".w.w.w.w", "w.w.w.w."]),
    ("BLACK", 100.0, [".b.....b", "b...b.b.", ".b...b.b", "..b.w...", "........", "w...w...", ".w.w...w", "w...w.w."]),
    ("BLACK", 100.0, [".b...b..", "..b...b.", ".....w.b", "....w...", ".b......", "w...w.w.", "...B....", "......w."]),
    ("WHITE", 6.6, ["........", "w...b.b.", "........", "..w.b...", ".w...b..", "....b...", ".w.....b", "..w...w."]),
    ("WHITE", 23.33, [".b...b..", "..b.b.b.", "...b...b", "..b.....", ".....w..", "w.b.w.w.", ".w.....w", "w...w..."]),
    ("BLACK", 0.05, START),    # almost no time left: must still answer quickly
]

def run_examples(script):
    player = ProgramPlayer(script, os.path.basename(script))
    ok = True
    for i, (color, t, grid) in enumerate(EXAMPLES, 1):
        text, used, err = player.move(grid, color, t, mode="SINGLE")
        if err is None:
            _, err = check_move(grid, color, text)
        if err is None and used > t:
            err = "used %.2fs of %.2fs" % (used, t)
        ok &= err is None
        print("example %d (%s, %.2fs): %s  [%.2fs cpu]" % (
            i, color, t, "OK " + " | ".join(text.strip().splitlines()) if err is None else "FAIL " + err, used))
    return ok

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", default=os.path.join(HERE, "homework.py"), help="program under test")
    ap.add_argument("--opponent", default="random", help="random | minimax:N | path to another homework.py")
    ap.add_argument("--games", type=int, default=4, help="games to play, alternating colors")
    ap.add_argument("--time", type=float, default=60.0, help="CPU seconds per side per game")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--verbose", action="store_true", help="print every move")
    ap.add_argument("--examples", action="store_true", help="only run the single-move examples")
    args = ap.parse_args()

    if args.examples:
        sys.exit(0 if run_examples(args.agent) else 1)

    agent = ProgramPlayer(args.agent, "agent")
    tally = {"agent": 0, "opponent": 0, "draw": 0}
    for g in range(args.games):
        opp = make_player(args.opponent, args.seed + g)
        agent_color = "BLACK" if g % 2 == 0 else "WHITE"
        black, white = (agent, opp) if agent_color == "BLACK" else (opp, agent)
        winner, reason, turns, clock = play_game(black, white, args.time, args.verbose)
        result = "draw" if winner is None else "agent" if winner == agent_color else "opponent"
        tally[result] += 1
        print("game %d: agent=%s vs %s -> %s after %d turns (%s); time left B %.1fs W %.1fs" % (
            g + 1, agent_color, opp.label, result.upper(), turns, reason, clock["BLACK"], clock["WHITE"]))
    print("agent %d, opponent %d, draws %d" % (tally["agent"], tally["opponent"], tally["draw"]))

if __name__ == "__main__":
    main()
