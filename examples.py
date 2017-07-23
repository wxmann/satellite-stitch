from datetime import datetime, time, timedelta

import nict_himawari
import rammb_slider


def himawari8_rammb(saveloc):
    now = datetime.utcnow()
    three_hrs_ago = now - timedelta(hours=3)
    sattime = datetime.combine(three_hrs_ago.date(), time(three_hrs_ago.hour))
    img = rammb_slider.himawari(sattime, zoom=3, product=2,
                                rangex=range(3, 7), rangey=range(1, 3), latlon=True)
    img.save(saveloc)


def goes16_rammb(saveloc):
    now = datetime.utcnow()
    three_hrs_ago = now - timedelta(hours=3)
    sattime = datetime.combine(three_hrs_ago.date(), time(three_hrs_ago.hour))
    img = rammb_slider.goes16(sattime, zoom=3, product=14,
                              rangex=range(3, 7), rangey=range(1, 3), latlon=True)
    img.save(saveloc)


def himawari8_nict(saveloc):
    now = datetime.utcnow()
    three_hrs_ago = now - timedelta(hours=3)
    sattime = datetime.combine(three_hrs_ago.date(), time(three_hrs_ago.hour))
    img = nict_himawari.himawari8(sattime, zoom=5, product='vis',
                                  rangex=range(10, 13), rangey=range(3, 6), boundaries=True)
    img.save(saveloc)


if __name__ == '__main__':
    loc = 'img.png'
    himawari8_nict(loc)
