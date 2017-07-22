from itertools import product

from core import stitch

PARENT_URL = 'http://rammb-slider.cira.colostate.edu/data/imagery'


def create(timestamp, zoom, band, rangex, rangey):
    rangex = tuple(rangex)
    rangey = tuple(rangey)

    url_map = {(x, y): rammb_img_url(timestamp, band, zoom, x, y)
               for x, y in product(rangex, rangey)}

    return stitch(url_map, imgmode='RGB')


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
