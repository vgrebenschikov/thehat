import asyncio
import sys
import logging

from robot.robot import Robot
import settings

settings.log.handlers[0].setFormatter(logging.Formatter('%(message)s', datefmt='%d-%m-%Y %H:%M:%S'))

async def main():
    r = Robot(uri=f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws')

    if len(sys.argv) > 1:
        await r.run(pnum=int(sys.argv[1]))
    else:
        await r.run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
