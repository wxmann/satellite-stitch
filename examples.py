from datetime import datetime, time

import rammb_himawari


def himawari8_rammb(saveloc):
    now = datetime.utcnow()
    three_hrs_ago = datetime.combine(now, time(now.hour - 3))
    img = rammb_himawari.create(three_hrs_ago, zoom=3, band=2,
                                rangex=range(3, 5), rangey=range(1, 3), latlon=True)
    img.save(saveloc)


if __name__ == '__main__':
    loc = 'img.png'
    himawari8_rammb(loc)
