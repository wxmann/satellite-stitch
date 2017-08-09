from datetime import datetime, timedelta, time

from stitch import rammb_slider


def main():
    now = datetime.utcnow()
    one_hr_ago = now - timedelta(hours=1)
    sattime = datetime.combine(one_hr_ago.date(), time(one_hr_ago.hour))
    img = rammb_slider.himawari(sattime, zoom=3, product=13,
                                rangex=range(2, 5), rangey=range(2, 4), latlon=True)
    img.crop_relative(0, 0, 0.8, 0.87)
    img.logo()
    img.timestamp_label()
    img.show()


if __name__ == '__main__':
    main()