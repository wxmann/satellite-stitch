from itertools import product as cartesian_product

from .core import stitch, overlay
from .postprocess import CIRAPostProcessor

PARENT_URL = 'http://rammb-slider.cira.colostate.edu/data'

_sat_himawari = 'himawari'
_sat_goes16 = 'goes-16'


def himawari(timestamp, zoom, product, rangex, rangey,
             boundaries=True, latlon=False):
    return _get_satellite_img(_sat_himawari, timestamp, zoom, product, rangex, rangey,
                              boundaries, latlon)


def goes16(timestamp, zoom, product, rangex, rangey,
           boundaries=True, latlon=False):
    return _get_satellite_img(_sat_goes16, timestamp, zoom, product, rangex, rangey,
                              boundaries, latlon)


def _get_satellite_img(sat, timestamp, zoom, product, rangex, rangey,
                       boundaries, latlon):
    sat_img = just_satellite(sat, timestamp, zoom, product, rangex, rangey)

    if boundaries:
        map_bg = map_boundaries(sat, zoom, rangex, rangey)
        sat_img = overlay(sat_img, map_bg)
    if latlon:
        latlon_bg = latlons(sat, zoom, rangex, rangey)
        sat_img = overlay(sat_img, latlon_bg)

    return CIRAPostProcessor(sat_img, timestamp)


def just_satellite(sat, timestamp, zoom, product, rangex, rangey):
    if isinstance(product, int):
        product = 'band_{}'.format(str(product).zfill(2))

    sat_urls = {(x, y): _rammb_img_url(timestamp, product, zoom, x, y, sat)
                for x, y in cartesian_product(rangex, rangey)}
    return stitch(sat_urls, 'RGB')


def map_boundaries(sat, zoom, rangex, rangey):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'map', sat)
                   for x, y in cartesian_product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def latlons(sat, zoom, rangex, rangey):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'lat', sat)
                   for x, y in cartesian_product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def _rammb_img_url(timestamp, product, zoom, xtile, ytile, sat):
    if sat == _sat_himawari:
        imgtype = 'himawari---full_disk'
        datetimestr = timestamp.strftime('%Y%m%d%H%M00')
    elif sat == _sat_goes16:
        imgtype = 'goes-16---full_disk'
        datetimestr = timestamp.strftime('%Y%m%d%H%M37')
    else:
        raise ValueError("Sat argument must be one of ({})".format(','.join((_sat_himawari, _sat_goes16))))

    datestr = timestamp.strftime('%Y%m%d')
    zoomstr = str(zoom).zfill(2)
    position = '{}_{}'.format(str(ytile).zfill(3), str(xtile).zfill(3))
    return PARENT_URL + '/imagery/{date}/{imgtype}/{product}/' \
                        '{datetime}/{zoom}/{position}.png'.format(date=datestr, imgtype=imgtype,
                                                                  product=product, datetime=datetimestr,
                                                                  zoom=zoomstr, position=position)


def _map_or_latlon_url(x, y, zoom, map_or_lat, sat):
    if sat == _sat_himawari:
        some_date_str = '20170620161000'
    elif sat == _sat_goes16:
        some_date_str = '20170620160038'
    else:
        raise ValueError("Sat argument must be one of ({})".format(','.join((_sat_himawari, _sat_goes16))))

    pos = '{}_{}'.format(str(y).zfill(3), str(x).zfill(3))
    return PARENT_URL + '/{type}/{sat}/full_disk/white/' \
                        '{some_date_str}/{zoom}/{pos}.png'.format(type=map_or_lat,
                                                                  zoom=str(zoom).zfill(2),
                                                                  pos=pos, sat=sat,
                                                                  some_date_str=some_date_str)
