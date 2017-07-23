import warnings
from itertools import product

import requests
from PIL import Image

from core import stitch, overlay

PARENT_URL = 'http://rammb-slider.cira.colostate.edu/data'

LOGO_URL = 'http://rammb-slider.cira.colostate.edu/images/cira_logo_200.png'


def himawari8(timestamp, zoom, band, rangex, rangey,
              boundaries=True, latlon=False, logo=True):
    rangex = tuple(rangex)
    rangey = tuple(rangey)

    sat_urls = {(x, y): _rammb_img_url(timestamp, band, zoom, x, y)
                for x, y in product(rangex, rangey)}

    sat_img = stitch(sat_urls, 'RGB')

    if boundaries:
        map_bg = map_boundaries(rangex, rangey, zoom)
        sat_img = overlay(sat_img, map_bg)
    if latlon:
        latlon_bg = latlons(rangex, rangey, zoom)
        sat_img = overlay(sat_img, latlon_bg)
    if logo:
        logo_img = ciralogo()
        if logo_img is not None:
            # put it in the bottom right
            simg_width, simg_height = sat_img.size
            limg_width, limg_height = logo_img.size

            posx = simg_width - limg_width
            posy = simg_height - limg_height
            sat_img = overlay(sat_img, logo_img, pos=(posx, posy))

    return sat_img


def map_boundaries(rangex, rangey, zoom):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'map') for x, y in product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def latlons(rangex, rangey, zoom):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'lat') for x, y in product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def ciralogo():
    resp = requests.get(LOGO_URL, stream=True)
    if resp is not None and resp.status_code == 200:
        resp.raw.decode_content = True
        return Image.open(resp.raw)
    else:
        warnings.warn('Cannot fetch CIRA logo')
        return None


def _rammb_img_url(timestamp, band, zoom, xtile, ytile):
    datestr = timestamp.strftime('%Y%m%d')
    imgtype = 'himawari---full_disk'
    bandstr = 'band_' + str(band).zfill(2)
    datetimestr = timestamp.strftime('%Y%m%d%H%M%S')
    zoomstr = str(zoom).zfill(2)
    position = '{}_{}'.format(str(ytile).zfill(3), str(xtile).zfill(3))
    return PARENT_URL + '/imagery/{date}/{imgtype}/{band}/' \
                        '{datetime}/{zoom}/{position}.png'.format(date=datestr, imgtype=imgtype,
                                                                  band=bandstr, datetime=datetimestr,
                                                                  zoom=zoomstr, position=position)


def _map_or_latlon_url(x, y, zoom, map_or_lat):
    pos = '{}_{}'.format(str(y).zfill(3), str(x).zfill(3))
    return PARENT_URL + '/{type}/himawari/' \
                        'full_disk/white/20170620161000/{zoom}/{pos}.png'.format(type=map_or_lat,
                                                                                 zoom=str(zoom).zfill(2),
                                                                                 pos=pos)
