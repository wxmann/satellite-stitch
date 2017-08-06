from itertools import product as cartesian_product

import sys

from PIL import Image

from stitch.core import stitch
from stitch.tests._common import image_equivalence_test, load_test_resource

if sys.version_info >= (3, 0):
    from unittest.mock import patch
else:
    from mock import patch


def _dummy_load():
    def func(path_map):
        xvals = [xy[0] for xy in path_map.keys()]
        yvals = [xy[1] for xy in path_map.keys()]
        minx, miny = min(xvals), min(yvals)

        return {
            (x, y): load_test_resource('imgs/({}_{}).jpg'.format(x - minx, y - miny))
            for (x, y) in path_map.keys()
        }

    return func


@image_equivalence_test
@patch('stitch.core.load_tiles')
def test_stitch(load):
    load.side_effect = _dummy_load()

    dummy_paths = {
        (x, y): 'http://dummy.com/({}_{}).png'.format(x, y)
        for x, y in cartesian_product(range(2, 5), range(3, 7))
    }

    actual = stitch(dummy_paths, 'RGB')
    expected = Image.open(load_test_resource('imgs/happypath_stitch_result.jpg'), 'r')
    return actual, expected
