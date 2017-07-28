from datetime import datetime, time, timedelta

import nict_himawari
import rammb_slider
from core import overlay
from utils import crop_relative, cira_rammb_logo, minimize


def himawari8_rammb_philippine_sea():
    now = datetime.utcnow()
    three_hrs_ago = now - timedelta(hours=3)
    sattime = datetime.combine(three_hrs_ago.date(), time(three_hrs_ago.hour))
    img = rammb_slider.himawari(sattime, zoom=3, product=14,
                                rangex=range(1, 4), rangey=range(1, 4), latlon=True)
    cropped = crop_relative(img, (0.3, 0.3, 0.95, 0.8))
    return cropped


def goes16_rammb():
    now = datetime.utcnow()
    three_hrs_ago = now - timedelta(hours=5)
    sattime = datetime.combine(three_hrs_ago.date(), time(three_hrs_ago.hour))
    img = rammb_slider.goes16(sattime, zoom=3, product=14,
                              rangex=range(3, 7), rangey=range(1, 3), latlon=True)
    return img


def himawari8_nict():
    now = datetime.utcnow()
    three_hrs_ago = now - timedelta(hours=3)
    sattime = datetime.combine(three_hrs_ago.date(), time(three_hrs_ago.hour))
    img = nict_himawari.himawari8(sattime, zoom=5, product='vis',
                                  rangex=range(8, 12), rangey=range(2, 5), boundaries=True)
    img = crop_relative(img, (0.25, 0.25, 1.0, 0.90))
    return img


if __name__ == '__main__':
    im = himawari8_rammb_philippine_sea()
    logo = cira_rammb_logo()
    minimize(logo, 0.8)
    result = overlay(im, logo, (im.width - logo.width, im.height - logo.height))
    result.show()
