from itertools import product as cartesian_product

import grequests

from .core import stitch, overlay
from .postprocess import CIRAPostProcessor

PARENT_URL = 'http://rammb-slider.cira.colostate.edu/data'

_sat_himawari = 'himawari'
_sat_goes16 = 'goes-16'


def himawari(timestamp, zoom, product, rangex, rangey,
             boundaries=True, latlon=False, crop=None):
    return _get_satellite_img(_sat_himawari, timestamp, zoom, product, rangex, rangey,
                              boundaries, latlon, crop)


def goes16(timestamp, zoom, product, rangex, rangey,
           boundaries=True, latlon=False, crop=None):
    return _get_satellite_img(_sat_goes16, timestamp, zoom, product, rangex, rangey,
                              boundaries, latlon, crop)


def _get_satellite_img(sat, timestamp, zoom, product, rangex, rangey,
                       boundaries, latlon, crop):
    sat_img, exact_timestamp = just_satellite(sat, timestamp, zoom, product, rangex, rangey)

    if boundaries:
        map_bg = map_boundaries(sat, zoom, rangex, rangey)
        sat_img = overlay(sat_img, map_bg)
    if latlon:
        latlon_bg = latlons(sat, zoom, rangex, rangey)
        sat_img = overlay(sat_img, latlon_bg)

    postprocessor = CIRAPostProcessor(sat_img, exact_timestamp)
    if crop:
        postprocessor.crop_relative(*crop)
    return postprocessor


def just_satellite(sat, timestamp, zoom, product, rangex, rangey):
    if isinstance(product, int):
        product = 'band_{}'.format(str(product).zfill(2))

    seconds = 0
    # HACK: the seconds value of GOES-16 imagery does not remain constant.
    if sat == _sat_goes16:
        seconds = _goes16_seconds_hack(sat, timestamp, zoom, product)
        timestamp = timestamp.replace(second=seconds)

    sat_urls = {(x, y): _rammb_img_url(timestamp, product, zoom, x, y, sat, seconds)
                for x, y in cartesian_product(rangex, rangey)}
    return stitch(sat_urls, 'RGB'), timestamp


def map_boundaries(sat, zoom, rangex, rangey):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'map', sat)
                   for x, y in cartesian_product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def latlons(sat, zoom, rangex, rangey):
    bg_map_urls = {(x, y): _map_or_latlon_url(x, y, zoom, 'lat', sat)
                   for x, y in cartesian_product(rangex, rangey)}
    return stitch(bg_map_urls, 'RGBA')


def _rammb_img_url(timestamp, product, zoom, xtile, ytile, sat, seconds=0):
    if sat == _sat_himawari:
        imgtype = 'himawari---full_disk'
    elif sat == _sat_goes16:
        imgtype = 'goes-16---full_disk'
    else:
        raise ValueError("Sat argument must be one of ({})".format(','.join((_sat_himawari, _sat_goes16))))

    datestr = timestamp.strftime('%Y%m%d')
    zoomstr = str(zoom).zfill(2)
    position = '{}_{}'.format(str(ytile).zfill(3), str(xtile).zfill(3))
    datetimestr = timestamp.replace(second=seconds).strftime('%Y%m%d%H%M%S')

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


def _goes16_seconds_hack(sat, timestamp, zoom, product):
    seconds = 0

    def successful_seconds(candidates):
        url_sec_map = {_rammb_img_url(timestamp, product, zoom, 0, 0, sat, candidate_sec): candidate_sec
                       for candidate_sec in candidates}

        reqs = (grequests.get(url) for url in url_sec_map.keys())
        resps = grequests.map(reqs, stream=True)
        return [url_sec_map[resp.url] for resp in resps if resp.status_code == 200]

    ordered_by_likelihood = [range(35, 40), range(30, 35), range(20, 25), range(25, 30),
                             # TODO should we even check these ranges?
                             range(0, 20), range(40, 60)]
    for second_candidates in ordered_by_likelihood:
        successes = successful_seconds(second_candidates)

        if successes:
            if len(successes) > 1:
                import warnings
                warnings.warn("Found more than one successful response, something seems to be wonky."
                              "Assume seconds corresponds with first successful response.")
            seconds = successes[0]
            break

    return seconds