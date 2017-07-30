from itertools import product as cartesian_product

from core import stitch, overlay
from postprocess import PostProcessor

BASE_URL = 'http://himawari8-dl.nict.go.jp/himawari8'


def himawari8(timestamp, zoom, product, rangex, rangey,
              boundaries=True):
    sat_urls = {(x, y): _get_product_url(timestamp, zoom, product, x, y)
                for x, y in cartesian_product(rangex, rangey)}
    sat_img = stitch(sat_urls, 'RGB')

    if boundaries:
        coastline_urls = {(x, y): _get_coastline_url(zoom, product, x, y)
                          for x, y in cartesian_product(rangex, rangey)}
        coastline_img = stitch(coastline_urls, 'RGBA')
        sat_img = overlay(sat_img, coastline_img)

    return PostProcessor(sat_img, timestamp)


_zoom_ref = {
    'D531106': {1: '1d', 2: '2d', 3: '4d', 4: '8d', 5: '16d', 6: '20d'},
    'INFRARED_FULL': {1: '1d', 2: '4d', 3: '8d'}
}

_product_ref = {
    'vis': 'D531106',
    'ir': 'INFRARED_FULL'
}


def _get_product_url(timestamp, zoom, product, x, y):
    prepend = _himawari_url_common(zoom, product)

    year = timestamp.year
    month = str(timestamp.month).zfill(2)
    day = str(timestamp.day).zfill(2)
    time = timestamp.time().strftime('%H%M00')
    return prepend + '/{year}/{month}/{day}/{time}_{x}_{y}.png'.format(year=year, month=month, day=day,
                                                                       time=time, x=x, y=y)


def _get_coastline_url(zoom, product, x, y):
    prepend = _himawari_url_common(zoom, product)
    return prepend + '/coastline/ffff00_{x}_{y}.png'.format(x=x, y=y)


def _himawari_url_common(zoom, product):
    try:
        product = _product_ref[product.lower()]
        zoom = _zoom_ref[product][zoom]
    except KeyError:
        raise ValueError("Invalid product {} or zoom {}".format(product, zoom))

    return BASE_URL + '/img/{product}/{zoom}/550'.format(product=product,
                                                         zoom=zoom)
