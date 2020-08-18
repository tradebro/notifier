import uvloop
import asyncio
from notifier import main


uvloop.install()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(main(aio_loop=loop))

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())
