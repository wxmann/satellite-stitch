from datetime import datetime, time

import rammb_himawari


def himawari8_rammb(saveloc):
    now = datetime.utcnow()
    last_hr = datetime.combine(now, time(now.hour - 1))
    img = rammb_himawari.create(last_hr, zoom=3, band=2,
                                rangex=range(3, 5), rangey=range(1, 3))
    img.save(saveloc)


if __name__ == '__main__':
    loc = 'img.png'
    himawari8_rammb(loc)
