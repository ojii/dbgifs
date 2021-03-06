import argparse
import asyncio
from collections import namedtuple
import logging
import os

from raven import Client
client = Client()

from database import Database
from server import build_web_app


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATES_DIR = os.path.join(THIS_DIR, 'templates')
DEFAULT_STATIC_DIR = os.path.join(THIS_DIR, 'static')


Config = namedtuple(
    'Config',
    'host port gifs_dir static_dir templates_dir scan_frequency'
)


def keep_calling(loop, frequency, func, *args, **kwargs):
    def schedule():
        logging.info("Scheduling to call {} in {}s".format(func, frequency))
        loop.call_later(
            frequency,
            handler,
        )

    def handler():
        logging.info("Calling {}".format(func))
        try:
            func(*args, **kwargs)
        except:
            client.captureException()
        finally:
            schedule()

    schedule()


def run(config):
    loop = asyncio.get_event_loop()

    database = Database(config.gifs_dir)
    webapp = build_web_app(config, database)

    keep_calling(loop, config.scan_frequency, database.scan)

    future = loop.create_server(webapp.make_handler, config.host, config.port)
    loop.run_until_complete(future)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gifs-dir')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--templates-dir', default=DEFAULT_TEMPLATES_DIR)
    parser.add_argument('--static-dir', default=DEFAULT_STATIC_DIR)
    parser.add_argument('--scan-frequency', type=int, default=5 * 60)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    config = Config(**{
        key.replace('-', '_'): var for key, var in vars(args).items()
    })

    run(config)


if __name__ == '__main__':
    main()
