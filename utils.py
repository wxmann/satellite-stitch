from __future__ import division

import warnings

from PIL import Image


def crop_relative(im, rel_box):
    for arg in rel_box:
        if arg < 0 or arg > 1.0:
            raise ValueError("Must supply in box 0 <= arg <= 1")

    left, top, right, bottom = rel_box
    width, height = im.size

    return im.crop((left * width, top * height,
                    right * width, bottom * height))


def minimize(im, ratio):
    im.thumbnail((im.width * ratio, im.height * ratio))


def cira_rammb_logo():
    import grequests
    cira_logo = 'http://rammb-slider.cira.colostate.edu/images/cira_logo_200.png'
    rammb_logo = 'http://rammb-slider.cira.colostate.edu/images/rammb_logo_150.png'

    reqs = (grequests.get(url) for url in (cira_logo, rammb_logo))
    resps = grequests.map(reqs, stream=True)
    logos = []
    for resp in resps:
        if resp is not None and resp.status_code == 200:
            resp.raw.decode_content = True
            logos.append(Image.open(resp.raw))
        else:
            warnings.warn('Cannot fetch logos: {}'.format(resp.url))
            return None

    return side_by_side(logos[0], logos[1], 'RGBA')


def side_by_side(im1, im2, mode, valign='bottom'):
    if valign not in ('top', 'bottom', 'center'):
        raise ValueError("`valign` argument must be one of `top`, `bottom`, or `center`")
    w1, h1 = im1.size
    w2, h2 = im2.size

    new_height = max(h1, h2)
    new_width = w1 + w2

    new_im = Image.new(mode, (new_width, new_height), color=None)

    def geth(hdiff):
        if valign == 'bottom':
            return hdiff
        elif valign == 'center':
            return hdiff / 2
        else:
            return 0

    if h2 < h1:
        new_im.paste(im1, (0, 0))
        new_im.paste(im2, (w1, geth(new_height - h2)))
    else:
        new_im.paste(im1, (0, geth(new_height - h1)))
        new_im.paste(im2, (w1, 0))

    return new_im
