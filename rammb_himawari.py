import os
import shutil
import tempfile
from datetime import datetime
from itertools import product

import grequests
from PIL import Image

PARENT_URL = 'http://rammb-slider.cira.colostate.edu/data/imagery'


def rammb_img_url(timestamp, band, zoom, xtile, ytile):
    datestr = timestamp.strftime('%Y%m%d')
    imgtype = 'himawari---full_disk'
    bandstr = 'band_' + str(band).zfill(2)
    datetimestr = timestamp.strftime('%Y%m%d%H%M%S')
    zoomstr = str(zoom).zfill(2)
    position = '{}_{}'.format(str(ytile).zfill(3), str(xtile).zfill(3))
    return PARENT_URL + '/{date}/{imgtype}/{band}/' \
                        '{datetime}/{zoom}/{position}.png'.format(date=datestr, imgtype=imgtype,
                                                                  band=bandstr, datetime=datetimestr,
                                                                  zoom=zoomstr, position=position)


def create(writeto, timestamp, zoom, band, rangex, rangey):
    rangex = tuple(rangex)
    rangey = tuple(rangey)

    resp_lookup = {rammb_img_url(timestamp, band, zoom, x, y): (x, y)
                   for x, y in product(rangex, rangey)}

    reqs = (grequests.get(url) for url in resp_lookup.keys())
    imgs = grequests.map(reqs, stream=True)

    with tempfile.TemporaryDirectory() as tmpd:
        tileloc_lookup = dict()
        for img in imgs:
            if img.status_code == 200:
                x, y = resp_lookup[img.url]
                filename = '{ts}_{band}_{zoom}_{x}_{y}.png'.format(ts=timestamp.strftime('%Y%m%d%H%M%S'),
                                                                   band=band, zoom=zoom,
                                                                   x=x, y=y)
                tile = os.sep.join([tmpd, filename])
                tileloc_lookup[(x, y)] = tile
                with open(tile, 'wb') as f:
                    img.raw.decode_content = True
                    shutil.copyfileobj(img.raw, f)

        result = combine(tileloc_lookup, rangex, rangey)
        result.save(writeto)


def combine(tilelookup, rangex, rangey):
    tiles = {(x, y): Image.open(tileloc) for ((x, y), tileloc) in tilelookup.items()}
    return TileArray.fromtiles(tiles, rangex, rangey).merge('RGB')


class StitchException(Exception):
    pass


class TileArray(object):
    @classmethod
    def fromtiles(cls, tilelookup, rangex, rangey):
        if not tilelookup:
            raise ValueError("Empty tiles")

        minx = min(rangex)
        miny = min(rangey)
        rows = len(rangey)
        cols = len(rangex)

        animg = tilelookup[next(iter(tilelookup.keys()))]
        imwidth, imheight = animg.size

        inst = cls(rows, cols, imwidth, imheight)
        for j in rangey:
            for i in rangex:
                joffset = j - miny
                ioffset = i - minx
                inst[joffset, ioffset] = tilelookup[i, j]
        return inst

    def __init__(self, rows, cols, cellwidth, cellheight):
        self._arr = list(list(None for i in range(cols)) for j in range(rows))
        self._rows = rows
        self._cols = cols
        self._cellwidth = cellwidth
        self._cellheight = cellheight

    def _check_access(self, key):
        if not isinstance(key, tuple) and len(key) != 2:
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


if __name__ == '__main__':
    create('/your/location/here',
           datetime(2017, 7, 21, 1, 30), zoom=3, band=2, rangex=range(3,5), rangey=range(1, 3))
