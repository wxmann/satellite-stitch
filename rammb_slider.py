import warnings
from itertools import product

import grequests
from PIL import Image

from core import stitch, overlay

PARENT_URL = 'http://rammb-slider.cira.colostate.edu/data'

CIRA_LOGO_URL = 'http://rammb-slider.cira.colostate.edu/images/cira_logo_200.png'

RAMMB_LOGO_URL = 'http://rammb-slider.cira.colostate.edu/images/rammb_logo_150.png'

_sat_himawari = 'himawari'
_sat_goes16 = 'goes-16'


def himawari(timestamp, zoom, band, rangex, rangey,
             boundaries=True, latlon=False, logo=True):

    return _get_satellite_img(_sat_himawari, timestamp, zoom, band, rangex, rangey,
                              boundaries, latlon, logo)


def goes16(timestamp, zoom, band, rangex, rangey,
           boundaries=True, latlon=False, logo=True):

    return _get_satellite_img(_sat_goes16, timestamp, zoom, band, rangex, rangey,
                              boundaries, latlon, logo)


def _get_satellite_img(sat, timestamp, zoom, band, rangex, rangey,
                       boundaries, latlon, logo):

    sat_img = just_satellite(sat, timestamp, zoom, band, rangex, rangey)

    if boundaries:
        map_bg = map_boundaries(sat, zoom, rangex, rangey)
        sat_img = overlay(sat_img, map_bg)
    if latlon:
        latlon_bg = latlons(sat, zoom, rangex, rangey)
        sat_img = overlay(sat_img, latlon_bg)
    if logo:
        logo_imgs = cira_rammb_logos()
        if logo_imgs is not None:
            # start from bottom right and paste left
            simg_width, simg_height = sat_img.size
            ypos = simg_height
            xpos = simg_width

            for logo_img in reversed(logo_imgs):
                limg_width, limg_height = logo_img.size
                xpos -= limg_width
                sat_img = overlay(sat_img, logo_img, pos=(xpos, ypos - limg_height))

    return sat_img


def just_satellite(sat, timestamp, zoom, band, rangex, rangey):
    rangex = tuple(rangex)
    rangey = tuple(rangey)

    sat_urls = {(x, y): _rammb_img_url(timestamp, band, zoom, x, y, sat)
                for x, y in product(rangex, rangey)}
    return stitch(sat_urls, 'RGB')


def map_boundaries(sat, zoom, rangex, rangey):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'map', sat)
                   for x, y in product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def latlons(sat, zoom, rangex, rangey):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'lat', sat)
                   for x, y in product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def cira_rammb_logos():
    reqs = (grequests.get(url) for url in (CIRA_LOGO_URL, RAMMB_LOGO_URL))
    resps = grequests.map(reqs, stream=True)
    logos = []
    for resp in resps:
        if resp is not None and resp.status_code == 200:
            resp.raw.decode_content = True
            logos.append(Image.open(resp.raw))
        else:
            warnings.warn('Cannot fetch logos: {}'.format(resp.url))
            return None
    return tuple(logos)


def _rammb_img_url(timestamp, band, zoom, xtile, ytile, sat):
    if sat == _sat_himawari:
        imgtype = 'himawari---full_disk'
        datetimestr = timestamp.strftime('%Y%m%d%H%M00')
    elif sat == _sat_goes16:
        imgtype = 'goes-16---full_disk'
        datetimestr = timestamp.strftime('%Y%m%d%H%M37')
    else:
        raise ValueError("Sat argument must be ({})".format(','.join((_sat_himawari, _sat_goes16))))

    datestr = timestamp.strftime('%Y%m%d')
    bandstr = 'band_' + str(band).zfill(2)
    zoomstr = str(zoom).zfill(2)
    position = '{}_{}'.format(str(ytile).zfill(3), str(xtile).zfill(3))
    return PARENT_URL + '/imagery/{date}/{imgtype}/{band}/' \
                        '{datetime}/{zoom}/{position}.png'.format(date=datestr, imgtype=imgtype,
                                                                  band=bandstr, datetime=datetimestr,
                                                                  zoom=zoomstr, position=position)


def _map_or_latlon_url(x, y, zoom, map_or_lat, sat):
    if sat == _sat_himawari:
        some_date_str = '20170620161000'
    elif sat == _sat_goes16:
        some_date_str = '20170620160038'
    else:
        raise ValueError("Sat argument must be ({})".format(','.join((_sat_himawari, _sat_goes16))))

    pos = '{}_{}'.format(str(y).zfill(3), str(x).zfill(3))
    return PARENT_URL + '/{type}/{sat}/' \
                        'full_disk/white/{some_date_str}/{zoom}/{pos}.png'.format(type=map_or_lat,
                                                                                  zoom=str(zoom).zfill(2),
                                                                                  pos=pos, sat=sat,
                                                                                  some_date_str=some_date_str)
