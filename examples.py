from datetime import datetime, time, timedelta

import rammb_himawari


def himawari8_rammb(saveloc):
    now = datetime.utcnow()
    three_hrs_ago = now - timedelta(hours=3)
    sattime = datetime.combine(three_hrs_ago.date(), time(three_hrs_ago.hour))
    img = rammb_himawari.create(sattime, zoom=3, band=2,
                                rangex=range(3, 7), rangey=range(1, 3), latlon=True)
    img.save(saveloc)


if __name__ == '__main__':
    loc = 'img.png'
    himawari8_rammb(loc)
