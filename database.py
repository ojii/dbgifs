from collections import defaultdict
import datetime
import logging
import os
import re

from dateutil.tz import tzlocal


SPLITTER = re.compile('-|_')


def filename_to_name(filename):
    nogif = filename[:-4]
    split = SPLITTER.split(nogif)
    return ' '.join(map(str.capitalize, split))


class GIF(object):
    def __init__(self, path, name, year, person, size):
        self.path = path
        self.filename = os.path.basename(path)
        self.name = name
        self.year = year
        self.person = person
        self.size = size

    def __repr__(self):
        return '<GIF:{}>'.format(self.path)

    def __eq__(self, other):
        if isinstance(other, GIF):
            return self.path == other.path
        else:
            return False


class Database(object):
    def __init__(self, source):
        self.source = source
        self.people = defaultdict(list) 
        self.gifs = []
        self.years = defaultdict(list)
        self.names = {}
        self.last_updated = datetime.datetime.now(tz=tzlocal())
        self.scan()

    def __repr__(self):
        return '<Database:{}>'.format(self.source)

    def scan(self):
        logging.info("Scan")
        count = 0
        for name in os.listdir(self.source):
            if name.endswith('.gif'):
                if self._load(name):
                    count += 1
        self.last_updated = datetime.datetime.now(tz=tzlocal())
        logging.info("Scan done ({} new GIFs)".format(count))

    def _load(self, filename):
        path = os.path.join(self.source, filename)
        stat = os.stat(path)
        year = datetime.datetime.fromtimestamp(stat.st_mtime).year
        person = SPLITTER.split(filename)[0]
        name = filename_to_name(filename)
        logging.info("Loading {}".format(name))
        gif = GIF(path, name, year, person, stat.st_size)
        if gif in self.gifs:
            logging.info("{} already found, skipping".format(name))
            return False
        self.gifs.append(gif)
        self.people[person].append(gif)
        self.years[year].append(gif)
        self.names[name] = gif
        logging.info("Loaded {}".format(name))
        return True
