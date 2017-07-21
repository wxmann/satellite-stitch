import os
import shutil
import tempfile
from itertools import product

import grequests

from common import combine

PARENT_URL = 'http://rammb-slider.cira.colostate.edu/data/imagery'


def create(timestamp, zoom, band, rangex, rangey):
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

        return combine(tileloc_lookup, rangex, rangey)


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
