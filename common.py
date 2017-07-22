import os
import random
import string
import tempfile

import grequests
import shutil
from PIL import Image


def stitch(pos_urls, imgmode='RGB'):
    with tempfile.TemporaryDirectory() as tmpd:
        tilelocs = save_tiles(pos_urls, tmpd)
        tileimgs = {(x, y): Image.open(tileloc) for ((x, y), tileloc) in tilelocs.items()}
        return TileArray.fromtiles(tileimgs).merge(imgmode)


def save_tiles(pos_url_map, saveloc):
    pos_lookup = {v: k for k, v in pos_url_map.items()}
    reqs = (grequests.get(url) for url in pos_lookup.keys())
    resps = grequests.map(reqs, stream=True)

    savedtile_lookup = dict()
    for resp in resps:
        if resp.status_code == 200:
            x, y = pos_lookup[resp.url]
            filename = '{x}{y}_{etc}.png'.format(x=x, y=y, etc=_randomstr(10))
            tile = os.sep.join([saveloc, filename])
            savedtile_lookup[x, y] = tile
            with open(tile, 'wb') as f:
                resp.raw.decode_content = True
                shutil.copyfileobj(resp.raw, f)

    return savedtile_lookup


def _randomstr(size):
    ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))


class StitchException(Exception):
    pass


class TileArray(object):
    @classmethod
    def fromtiles(cls, tileimgs):
        if not tileimgs:
            raise ValueError("Empty tiles")

        xpos = [pos[0] for pos in tileimgs.keys()]
        ypos = [pos[1] for pos in tileimgs.keys()]
        minx, maxx = min(*xpos), max(*xpos)
        miny, maxy = min(*ypos), max(*ypos)
        rangex = range(minx, maxx + 1)
        rangey = range(miny, maxy + 1)
        rows = maxy - miny + 1
        cols = maxx - minx + 1

        animg = next(iter(tileimgs.values()))
        imwidth, imheight = animg.size

        inst = cls(rows, cols, imwidth, imheight)
        for j in rangey:
            for i in rangex:
                joffset = j - miny
                ioffset = i - minx
                inst[joffset, ioffset] = tileimgs[i, j]
        return inst

    def __init__(self, rows, cols, cellwidth, cellheight):
        self._arr = list(list(None for i in range(cols)) for j in range(rows))
        self._rows = rows
        self._cols = cols
        self._cellwidth = cellwidth
        self._cellheight = cellheight

    def _check_access(self, key):
        if not isinstance(key, (list, tuple)) and len(key) != 2:
            raise IndexError("Tile array must be indexed by two items")

    def __getitem__(self, item):
        self._check_access(item)
        return self._arr[item[0]][item[1]]

    def __setitem__(self, key, value):
        self._check_access(key)
        self._arr[key[0]][key[1]] = value

    @property
    def height(self):
        return self._cellheight * self._rows

    @property
    def width(self):
        return self._cellwidth * self._cols

    def merge(self, mode='RGB'):
        output = Image.new(mode, (self.width, self.height))
        for i in range(self._rows):
            for j in range(self._cols):
                xpos = j * self._cellwidth
                ypos = i * self._cellheight
                output.paste(self[i, j], (xpos, ypos))
        return output
