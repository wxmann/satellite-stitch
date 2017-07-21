from datetime import datetime

import rammb_himawari


def himawari8_rammb(saveloc):
    img = rammb_himawari.create(datetime(2017, 7, 21, 1, 30), zoom=3, band=2,
                                rangex=range(3, 5), rangey=range(1, 3))
    img.save(saveloc)


if __name__ == '__main__':
    loc = '/your/loc/here/img.png'
    himawari8_rammb(loc)
