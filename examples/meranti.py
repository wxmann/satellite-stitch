from datetime import datetime

from stitch import nict_himawari


def main():
    sattime = datetime(2016, 9, 13, 8, 30)
    img = nict_himawari.vis(sattime, zoom=5,
                            rangex=range(4, 7), rangey=range(4, 6))
    img.crop_relative(0.2, 0, 0.85, 0.85)
    img.logo()
    img.timestamp_label()
    img.show()


if __name__ == '__main__':
    main()
