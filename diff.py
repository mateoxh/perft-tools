#!/usr/bin/python3

import subprocess
import itertools
import argparse
import chess
import re

parser = argparse.ArgumentParser()
parser.add_argument("ce",  help="Path to correct engine")
parser.add_argument("te",  help="Path to engine to test")
parser.add_argument("fen",  help="FEN string")

branch = []
args = parser.parse_args()
board = chess.Board(args.fen)

def get_divide(path, depth):
    with subprocess.Popen(
            path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True
            ) as process:

        process.stdin.write("position fen %s\n" % board.fen())
        process.stdin.write("go perft %d\n" % depth)
        process.stdin.close()

        return process.stdout.read()

def bad_moves(s, o):
    p = re.compile("\s*[a-h][1-8][a-h][1-8][nbrq]{0,1}\s*:\s*\d+")

    sl = [x for x in s.split("\n") if p.match(x)]
    ol = [x for x in o.split("\n") if p.match(x)]

    sd = {x[:x.index(":")].strip():x[x.index(":") + 1:].strip() for x in sl}
    od = {x[:x.index(":")].strip():x[x.index(":") + 1:].strip() for x in ol}

    illegal = [k for k in od if k not in sd]
    wrong = [k for k in sd if k not in od or sd[k] != od[k]]

    return illegal + wrong

def track(depth):
    for d in range(depth, 0, -1):
        l = bad_moves(get_divide(args.ce, d), get_divide(args.te, d))

        if l:
            branch.append(l[0])

            try:
                board.push_uci(l[0])
            except chess.IllegalMoveError:
                break

    print(" => ".join(branch))
    print("FEN: " + board.fen())

for d in itertools.count(1):
    l = bad_moves(get_divide(args.ce, d), get_divide(args.te, d))

    print("Depth %d: " % d, end="")
    if not l:
        print("OK")
    else:
        print("ERROR")
        print("Bad moves: " + ", ".join(l))
        print("Following %s..." % l[0])

        try:
            board.push_uci(l[0])
        except chess.IllegalMoveError:
            pass
        else:
            branch.append(l[0])

        track(d - 1 if d > 1 else 1)
        break
