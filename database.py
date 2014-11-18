from collections import defaultdict
import datetime
import os
import re


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
        self.scan()

    def __repr__(self):
        return '<Database:{}>'.format(self.source)

    def scan(self):
        for name in os.listdir(self.source):
            if name.endswith('.gif'):
                self._load(name)

    def _load(self, filename):
        path = os.path.join(self.source, filename)
        stat = os.stat(path)
        year = datetime.datetime.fromtimestamp(stat.st_mtime).year
        person = SPLITTER.split(filename)[0]
        name = filename_to_name(filename)
        gif = GIF(path, name, year, person, stat.st_size)
        if gif in self.gifs:
            return
        self.gifs.append(gif)
        self.people[person].append(gif)
        self.years[year].append(gif)
        self.names[name] = gif
