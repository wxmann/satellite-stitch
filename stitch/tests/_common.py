import math
import operator
import os
from functools import reduce, wraps

from PIL import ImageChops, Image


def rmsdiff(im1, im2):
    "Calculate the root-mean-square difference between two images"

    h = ImageChops.difference(im1, im2).histogram()

    # calculate rms
    return math.sqrt(reduce(operator.add,
        map(lambda h, i: h*(i**2), h, range(256))
    ) / (float(im1.size[0]) * im1.size[1]))


def imgs_eq(im1, im2, tolerance=2):
    if im1.size != im2.size:
        return False
    return rmsdiff(im1, im2) < tolerance


def path_of_test_resource(filename):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.sep.join([this_dir, filename])


def image_equivalence_test(test_func):
    @wraps(test_func)
    def new_test_func(*args, **kwargs):
        actual, expected = test_func(*args, **kwargs)

        try:
            assert imgs_eq(actual, expected, tolerance=2)
        except AssertionError:
            actual.show(title='actual')
            expected.show(title='expected')
            ImageChops.difference(actual, expected).show(title='diff')
            raise

    return new_test_func


def open_image(file):
    return Image.open(path_of_test_resource(file), 'r')


# just a utility
def save_image(im, file):
    im.save(path_of_test_resource(file), subsampling=0, quality=100)

