from datetime import datetime, time, timedelta

from stitch import rammb_slider


def main():
    now = datetime.utcnow()
    one_hr_ago = now - timedelta(hours=2)
    sattime = datetime.combine(one_hr_ago.date(), time(one_hr_ago.hour))
    img = rammb_slider.goes16(sattime, zoom=3, product=14,
                              rangex=range(3, 7), rangey=range(1, 4), latlon=True)
    img.crop_relative(0, 0, 1, 0.9)
    img.logo()
    img.timestamp_label()
    img.colorbar()
    img.show()


if __name__ == '__main__':
    main()
