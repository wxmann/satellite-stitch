from PIL import Image


class StitchException(Exception):
    pass


def combine(tilelookup, rangex, rangey):
    tiles = {(x, y): Image.open(tileloc) for ((x, y), tileloc) in tilelookup.items()}
    return TileArray.fromtiles(tiles, rangex, rangey).merge('RGB')


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
