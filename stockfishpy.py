#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Simple Python Stockfish UCI wrapper
    UCI chess engine http://www.stockfishchess.com/ 

    :copyright: (c) 2016 by Dani Korniliev
    :license: GNU General Public License, see LICENSE for more details.
"""


import subprocess
import sys


class Engine(subprocess.Popen):
    """
    Initiates Stockfish Chess Engine with default param and depth = '12' requires stockfish path 

    'param' & setoption function refers to https://github.com/iamjarret/pystockfish#details 
    'param' allows parameters to be specified by a dictionary object with 'Name' and 'value'
    with value as an integer.

    i.e. the following explicitly sets the default parameters

    default_param = {
            "Write Debug Log": "false",
            "Contempt": 0,
            "Threads": 1,
            "Hash": 16,
            "Min Split Depth": 0,
            "Ponder": "false",
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 30,
            "Minimum Thinking Time": 20,
            "Slow Mover": 80,
            "Nodestime": 0,
            "UCI_Chess960": "false",
            "SyzygyPath": "",
            "SyzygyProbeDepth": 1,
            "Syzygy50MoveRule": 'true',
            "SyzygyProbeLimit": 6
        }


    """
    def __init__(self, engine_path="", depth=12, param=None):
        subprocess.Popen.__init__(self, engine_path, universal_newlines=True,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

        default_param = {
            "Write Debug Log": "false",
            "Contempt": 0,
            "Threads": 1,
            "Hash": 16,
            "Min Split Depth": 0,
            "Ponder": "false",
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 30,
            "Minimum Thinking Time": 20,
            "Slow Mover": 80,
            "Nodestime": 0,
            "UCI_Chess960": "false",
            "SyzygyPath": "",
            "SyzygyProbeDepth": 1,
            "Syzygy50MoveRule": 'true',
            "SyzygyProbeLimit": 6
        }

        default_param.update(param)
        self.param = default_param
        for name, value in list(default_param.items()):
            self.setoption(name, value)

        self.uciok()
        self.depth = str(depth)

    def send(self, command):
        self.stdin.write(command + '\n')
        self.stdin.flush()

    def flush(self):
        self.stdout.flush()

    def uciok(self):
        self.send('uci')
        while True:
            line = self.stdout.readline().strip()
            if line == 'uciok':
                return line

    def setoption(self, optionname, value):
        """ Update default_param dict """
        self.send('setoption name %s value %s' % (optionname, str(value)))
        stdout = self.isready()
        if stdout.find('No such') >= 0:
            print("stockfish was unable to set option %s" % optionname)

    def setposition(self, position):
        """

        The move format is in long algebraic notation.

        Takes list of stirngs = ['e2e4', 'd7d5']
        OR
        FEN = 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'

        """
        try:
            if isinstance(position, list):
                self.send('position startpos moves {}'.format(
                    self.__listtostring(position)))
                self.isready()
            else:
                self.send('position fen {}'.format(position))
                self.isready()
        except Exception as e:
            print '\nCheck position correctness\n'
            sys.exit(e.message)

    def __listtostring(self, move):
        return ' '.join(move).strip()

    def go(self):
        self.send('go depth {}'.format(self.depth))

    def isready(self):
        self.send('isready')
        while True:
            line = self.stdout.readline().strip()
            if line == 'readyok':
                return line

    def ucinewgame(self):
        self.send('ucinewgame')
        self.isready()

    def bestmove(self):
        info = ""
        self.go()
        while True:
            line = self.stdout.readline().strip().split(' ')
            if line[0] == 'bestmove':
                if self.param['Ponder'] == 'true':
                    ponder = line[3]
                else:
                    ponder = None
                return {'move': line[1], 'ponder': ponder, 'info': info}
            info = line
