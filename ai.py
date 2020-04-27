#!/usr/bin/env python3
from asyncio import (get_event_loop, ensure_future, gather, sleep)
import json
import sys
import getopt
import logging
import requests
from typing import (Optional)

from game import message
from robot.robot import Robot
import settings

settings.log.handlers[0].setFormatter(logging.Formatter('%(message)s', datefmt='%d-%m-%Y %H:%M:%S'))


def results(res, names=None, prefix=None):
    if res is None:
        return

    print()
    for h in (('Player', 'Total', 'Explained', 'Guessed'), ('-' * 14, '-' * 9, '-' * 9, '-' * 9)):
        print(f"{h[0]:<14s} {h[1]:>9s} {h[2]:>9s} {h[3]:>9s}")

    if not names:
        names = list(res['score'].keys())

    if not prefix:
        prefix = names

    for i in range(0, len(names)):
        sc = res['score'][names[i]]
        print(f"{prefix[i]:14s} {sc['total']:9d} {sc['explained']:9d} {sc['guessed']:9d}")


class Options:

    id: Optional[str]
    autoplay: Optional[int]
    robots: Optional[int]
    speed: int
    site: str
    reset: bool

    @staticmethod
    def usage(err=None):
        if err:
            print(f'Error: {err}', file=sys.stderr)

        print(f"""
USAGE:
    {sys.argv[0]} [<flags>] [<game-id>]
Flags:
    -h, --help          Help (this)
    -a, --auto  <num>   Auto-play with <num> players (same, as -p <num> -r <num>)
    -p, --play  <num>   Invoke play command after <num> players connected
    -r, --run   <num>   Run <num> local players
    -s, --speed <speed> Run with <speed>, 0-20, 0 - the fastest (also imply -t <speed>)
    -n, --name  <name>  Set new game name
    -t, --timer <sec>   Set turn timer to <sec> seconds
    -w, --words <wnum>  Set words number to <wnum>
    -u, --site  <uri>   Set server host to <uri> (may be with port)
    -R, --reset         Reset existing game
""", file=sys.stderr)
        sys.exit(1)

    def __init__(self, argv):
        self.id = None
        self.autoplay = None
        self.robots = None
        self.speed = 0
        self.name = None
        self.timer = 1
        self.words = 6
        self.site = f'http://{settings.SITE_HOST}:{settings.SITE_PORT}'
        self.reset = False

        try:
            opts, args = getopt.getopt(argv[1:],
                                       "ha:p:r:s:n:t:w:u:R",
                                       [
                                           'help',
                                           'auto=',
                                           'play=',
                                           'run=',
                                           'speed=',
                                           'name=',
                                           'timer=',
                                           'words=',
                                           'site=',
                                           'reset'
            ])
        except getopt.GetoptError as err:
            # print help information and exit:
            Options.usage(err)
            return

        for o, a in opts:
            if o in ("-h", "--help"):
                Options.usage()
            elif o in ("-a", "--auto"):
                self.autoplay = int(a)
                self.robots = int(a)
            elif o in ("-p", "--play"):
                self.autoplay = int(a)
            elif o in ("-r", "--run"):
                self.robots = int(a)
            elif o in ("-s", "--speed"):
                self.speed = int(a)
            elif o in ("-n", "--name"):
                self.name = a
            elif o in ("-t", "--timer"):
                self.timer = int(a)
            elif o in ("-w", "--words"):
                self.words = int(a)
            elif o in ("-u", "--site"):
                self.site = a
            elif o in ("-R", "--reset"):
                self.reset = True
            else:
                Options.usage(f"unhandled option {o}")

        if len(args) > 1:
            Options.usage('Only one <game-id> can be specified')

        if len(args):
            self.id = args[0]

    def args(self):
        return {
            'name': self.name,
            'id': self.id,
            'timer': self.timer,
            'numwords': self.words,
            'uri': self.site,
            'idx': 0 if self.robots else None,
            'reset': self.reset
        }


async def main():
    opts = Options(sys.argv)

    r = Robot(**opts.args())
    try:
        if opts.id is None:
            """Create new game if id was not specified"""

            opts.id = await r.newgame()
        else:
            """Check if game exists"""

            if opts.id != await r.checkgame(opts.id):
                print('Game id miss-matched', file=sys.stderr)
                sys.exit(2)

    except Exception as e:
        print(f'Failed to acquire game: {e}')
        sys.exit(3)

    if opts.robots:
        rbs = [r]
        wrk = [ensure_future(r.run(pnum=opts.autoplay))]

        await sleep(0.2)  # Leader process should be able to reset game

        for i in range(1, opts.robots):
            r = Robot(uri=opts.site, idx=i, id=opts.id)
            rbs.append(r)
            wrk.append(ensure_future(r.run()))

        await gather(*wrk)
        results(wrk[0].result(), [r.pname for r in rbs], [r.id_prefix for r in rbs])
    else:
        res = await r.run(pnum=opts.autoplay)
        results(res)

if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())
