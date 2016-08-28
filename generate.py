#!/usr/bin/python3
{'You need Python 2.7+ or Python 3.1+'}

import sys
import chess

Chess960 = True

if __name__ == '__main__':
    for line in sys.stdin:
        fen = line.rstrip().split(';')[0]
        board = chess.Board(fen, Chess960)
        for move in board.legal_moves:
            board.push(move)
            print(board.shredder_fen() if Chess960 else board.fen())
            board.pop()
