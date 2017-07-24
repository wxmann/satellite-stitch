import os
import random
import string
import tempfile
import warnings
import io

import grequests
import shutil
from PIL import Image


def stitch(pos_urls, mode, tempfiles=False):
    if tempfiles:
        with tempfile.TemporaryDirectory() as tmpd:
            tilelocs = save_tiles(pos_urls, tmpd)
            tileimgs = {(x, y): Image.open(tileloc) for ((x, y), tileloc) in tilelocs.items()}
            return TileArray.fromtiles(tileimgs).merge(mode)
    else:
        tilebufs = load_tiles(pos_urls)
        tileimgs = {(x, y): Image.open(buf) for ((x, y), buf) in tilebufs.items()}
        return TileArray.fromtiles(tileimgs).merge(mode)


def load_tiles(pos_url_map):
    return _load_tile_inner(pos_url_map,
                            lambda resp, x, y: io.BytesIO(resp.content))


def save_tiles(pos_url_map, savedir):

    def savetodisk(resp, x, y):
        filename = '{x}_{y}_{etc}.png'.format(x=x, y=y, etc=_randomstr(10))
        savedtile_loc = os.sep.join([savedir, filename])
        with open(savedtile_loc, 'wb') as f:
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)
        return savedtile_loc

    return _load_tile_inner(pos_url_map, savetodisk)


def _load_tile_inner(pos_url_map, process_response):
    pos_lookup = {v: k for k, v in pos_url_map.items()}
    reqs = (grequests.get(url) for url in pos_lookup.keys())
    resps = grequests.map(reqs, stream=True)
    tiles = dict()
    for resp in resps:
        x, y = pos_lookup[resp.url]
        if resp is not None and resp.status_code == 200:
            tiles[x, y] = process_response(resp, x, y)
        else:
            warnings.warn('Error in getting tile at position: ({},{}), this image might '
                          'not stitch correctly'.format(x, y))
    return tiles


def _randomstr(size):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))


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
        if not isinstance(key, (list, tuple)) or len(key) != 2:
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

    def merge(self, mode):
        output = Image.new(mode, (self.width, self.height))
        for i in range(self._rows):
            for j in range(self._cols):
                xpos = j * self._cellwidth
                ypos = i * self._cellheight
                output.paste(self[i, j], (xpos, ypos))
        return output


def overlay(bottom, top, pos=(0, 0)):
    result = Image.new(bottom.mode, bottom.size)
    result.paste(bottom, (0, 0))
    top_mask = top.convert('RGBA')
    result.paste(top, pos, top_mask)
    return result
