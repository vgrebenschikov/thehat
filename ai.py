from asyncio import (get_event_loop, ensure_future, gather)

import sys
import logging

from robot.robot import Robot
import settings

settings.log.handlers[0].setFormatter(logging.Formatter('%(message)s', datefmt='%d-%m-%Y %H:%M:%S'))


async def main():
    uri = f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws'

    if len(sys.argv) == 3:
        wrk = []
        pnum = int(sys.argv[1])
        for i in range(0, pnum):
            av = {}
            if i == 0:
                av['pnum'] = pnum
            r = Robot(uri=uri)
            wrk.append(ensure_future(r.run(**av)))

        await gather(*wrk)
    if len(sys.argv) == 2:
        r = Robot(uri=uri)
        await r.run(pnum=int(sys.argv[1]))
    else:
        await r.run()

if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())
