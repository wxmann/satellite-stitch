import warnings

from PIL import Image

from core import side_by_side, overlay


class PostProcessor(object):
    def __init__(self, im):
        self.original = im
        self._processed = im.copy()

    def save(self, *args, **kwargs):
        self._processed.save(*args, **kwargs)

    def show(self, *args, **kwargs):
        self._processed.show(*args, **kwargs)

    def crop_relative(self, left, top, right, bottom):
        for arg in (left, top, right, bottom):
            if arg < 0 or arg > 1.0:
                raise ValueError("Must supply in box 0 <= arg <= 1")

        width, height = self._processed.size
        self._processed = self._processed.crop((left * width, top * height,
                                                right * width, bottom * height))

    def minimize(self, width, height):
        self._processed.thumbnail((width, height))


class CIRAPostProcessor(PostProcessor):
    def __init__(self, im):
        super(CIRAPostProcessor, self).__init__(im)

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

    def cira_rammb_logo(self):
        logo = CIRAPostProcessor._get_cira_rammb_logo()
        width, height = self._processed.size
        self._processed = overlay(self._processed, logo, (width - logo.width, height - logo.height))