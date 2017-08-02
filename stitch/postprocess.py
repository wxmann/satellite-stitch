import warnings

from PIL import Image, ImageFont, ImageDraw

from .core import side_by_side, overlay, resource_path


class PostProcessor(object):
    def __init__(self, im, timestamp):
        self.original = im
        self._processed = im.copy()
        self._timestamp = timestamp

    def save(self, *args, **kwargs):
        self._processed.save(*args, **kwargs)

    def show(self, *args, **kwargs):
        self._processed.show(*args, **kwargs)

    def crop_relative(self, left, top, right, bottom):
        self._check_arg_range(left, top, right, bottom)

        width, height = self._processed.size
        self._processed = self._processed.crop((left * width, top * height,
                                                right * width, bottom * height))

    def minimize(self, width, height):
        self._processed.thumbnail((width, height))

    def timestamp_label(self, breadth=0.2, padding=0.01, **text_kw):
        for remove_kw in ('xy', 'text', 'font'):
            if remove_kw in text_kw:
                text_kw.pop(remove_kw)

        drawer = ImageDraw.Draw(self._processed)
        text = self._timestamp.isoformat(sep=' ') + ' UTC'

        dummy_obj = Image.new('RGB', self._processed.size)
        x, _, target_size = self._placement(dummy_obj, 'bottom-left', breadth, padding)

        width, height = 0, 0
        fontsize = 1
        font = None
        while width < target_size.width and height < target_size.height:
            font = ImageFont.truetype(resource_path('Verdana.ttf'), fontsize)
            width, height = font.getsize(text)
            fontsize += 1

        if font is None:
            raise ValueError("Unexpected error: can't figure the font size")

        y = self._round((1 - padding) * self._processed.height - height)
        drawer.text((x, y), text, font=font, **text_kw)

    def _check_arg_range(self, *args, minval=0.0, maxval=1.0):
        for arg in args:
            if arg < minval or arg > maxval:
                raise ValueError("Must supply 0 <= arg <= 1")

    def _check_breadth_and_padding(self, breadth, padding):
        self._check_arg_range(breadth, padding, 0.0, 1.0)

        if breadth + 2 * padding > 1:
            raise ValueError("Supplied breadth and padding forces overlaid item to be out of bounds")

    def _placement(self, obj, corner, breadth, padding):
        self._check_breadth_and_padding(breadth, padding)

        if corner not in ('top-left', 'top-right',
                          'bottom-left', 'bottom-right'):
            raise ValueError("Invalid corner: {}".format(corner))

        imgwidth, imgheight = self._processed.size

        padding_abs = min(imgheight, imgwidth) * padding
        target_dims = imgwidth * breadth, imgheight * breadth
        resized = obj.copy()
        resized.thumbnail(target_dims)

        if 'left' in corner:
            x = self._round(0 + padding_abs)
        else:
            x = self._round(imgwidth - padding_abs - resized.width)

        if 'top' in corner:
            y = self._round(0 + padding_abs)
        else:
            y = self._round(imgheight - padding_abs - resized.height)

        return x, y, resized

    def _round(self, arg):
        if isinstance(arg, float):
            return int(round(arg))
        return arg


class CIRAPostProcessor(PostProcessor):
    def __init__(self, im, timestamp):
        super(CIRAPostProcessor, self).__init__(im, timestamp)

    @staticmethod
    def _get_cira_rammb_logo():
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

    def logo(self, breadth=0.2, padding=0.01):
        logo = CIRAPostProcessor._get_cira_rammb_logo()
        if logo is not None:
            x, y, logo_resized = self._placement(logo, 'bottom-right', breadth, padding)
            self._processed = overlay(self._processed, logo_resized, (x, y))


class NICTPostProcessor(PostProcessor):
    def __init__(self, im, timestamp):
        super(NICTPostProcessor, self).__init__(im, timestamp)

    def logo(self, breadth=0.2, padding=0.01):
        logoimg = Image.open(resource_path('logo_nict.png'), 'r')
        x, y, logo_resized = self._placement(logoimg, 'bottom-right', breadth, padding)
        self._processed = overlay(self._processed, logo_resized, (x, y))
