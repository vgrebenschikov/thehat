from asyncio import (get_event_loop, ensure_future, gather, sleep)

import sys
import logging

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


async def main():
    uri = f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws'

    if len(sys.argv) == 3:
        pnum = int(sys.argv[1])
        r = Robot(uri=uri, idx=0)
        rbs = [r]
        gid = await r.newgame(name='Secret Tea', timer=1)
        wrk = [ensure_future(r.run(pnum=pnum))]

        await sleep(0.2)  # Leader process should be able to reset game

        for i in range(1, pnum):
            r = Robot(uri=uri, idx=i, id=gid)
            rbs.append(r)
            wrk.append(ensure_future(r.run()))

        await gather(*wrk)
        results(wrk[0].result(), [r.pname for r in rbs], [r.id_prefix for r in rbs])

    elif len(sys.argv) == 2:
        r = Robot(uri=uri, id="00000000-0000-0000-0000-000000000000")
        res = await r.run(pnum=int(sys.argv[1]))
        results(res)

    else:
        r = Robot(uri=uri)
        res = await r.run()
        results(res)

if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())
