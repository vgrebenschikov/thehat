import asyncio
import sys

from robot.robot import Robot
import settings


async def main():
    r = Robot(uri=f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws')

    if len(sys.argv) > 1:
        await r.run(pnum=int(sys.argv[1]))
    else:
        await r.run()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
