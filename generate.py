#!/usr/bin/python3

from __future__ import print_function  # Python 2.7 compatibility
{'You need Python 2.7+ or Python 3.1+'}  # Syntax error on earlier versions

import sys
import subprocess
import chess

# Configure here
Chess960 = True
Engine = '../Stockfish/master'
Options = {'Hash': 64, 'Threads': 7}
Cutoff = 50  # expressed in cp
TimeControl = {'depth': 13, 'nodes': None, 'movetime': 1000}

class UCIEngine():
    def __init__(self, engine):
        self.process = subprocess.Popen(engine, stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, universal_newlines=True, bufsize=1)
        self.writeline('uci')
        self.options = []
        while True:
            line = self.readline()
            if line.startswith('option name '):
                tokens = line.split()
                name = tokens[2:tokens.index('type')]
                self.options.append(' '.join(name))
            elif line == 'uciok':
                break

    def readline(self):
        return self.process.stdout.readline().rstrip()

    def writeline(self, string):
        self.process.stdin.write(string + '\n')

    def setoptions(self, options):
        for name in options:
            value = options[name]
            if type(value) is bool:
                value = str(value).lower()
            self.writeline('setoption name {} value {}'.format(name, value))

    def isready(self):
        self.writeline('isready')
        while self.readline() != 'readyok':
            pass

    def newgame(self):
        self.writeline('ucinewgame')

    def go(self, args):
        tokens = ['go']
        for name in args:
            if args[name] is not None:
                tokens += [name, str(args[name])]
        self.writeline(' '.join(tokens))

        score = None
        while True:
            line = self.readline()
            if line.startswith('info'):
                i = line.find('score ')
                if i != -1:
                    tokens = line[(i + len('score ')):].split()
                    assert len(tokens) >= 2
                    if tokens[0] == 'cp':
                        if len(tokens) == 2 or not tokens[2].endswith('bound'):
                            score = int(tokens[1])
                    elif tokens[0] == 'mate':
                        score = math.copysign(Cutoff, int(tokens[1]))
            elif line.startswith('bestmove'):
                return line.split()[1], score

    def quit(self):
        self.writeline('quit')
        self.process.wait()


if __name__ == '__main__':
    uciEngine = UCIEngine(Engine)
    uciEngine.setoptions(Options)

    with open(sys.argv[1], 'r') as inFile, open(sys.argv[2], 'w') as outFile:
        for line in inFile:
            fen = line.rstrip().split(';')[0]
            board = chess.Board(fen, Chess960)
            uciEngine.newgame()
            print('processing:', fen)

            for move in board.legal_moves:
                board.push(move)
                childFen = board.shredder_fen() if Chess960 else board.fen()
                board.pop()

                uciEngine.writeline('position fen ' + childFen)
                uciEngine.isready()
                bestmove, score = uciEngine.go(TimeControl)

                if abs(score) < Cutoff:
                    print(childFen, file=outFile)

    uciEngine.quit()
