import os
from itertools import product as cartesian_product

import sys

import pytest
from PIL import Image

from stitch.core import stitch, StitchException
from stitch.tests._common import image_equivalence_test, path_of_test_resource

if sys.version_info >= (3, 0):
    from unittest.mock import patch
else:
    from mock import patch


def _dummy_load(exclude_tiles=()):
    def func(path_map):
        xvals = [xy[0] for xy in path_map.keys()]
        yvals = [xy[1] for xy in path_map.keys()]
        minx, miny = min(xvals), min(yvals)

        return {
            (x, y): path_of_test_resource('imgs/({}_{}).jpg'.format(x - minx, y - miny))
            for (x, y) in path_map.keys()
            if (x, y) not in exclude_tiles
        }

    return func


def _dummy_save():
    from shutil import copyfile

    def func(path_map, tmpdir):
        xvals = [xy[0] for xy in path_map.keys()]
        yvals = [xy[1] for xy in path_map.keys()]
        minx, miny = min(xvals), min(yvals)

        result = {}
        for (x, y) in path_map.keys():
            relpath = '({}_{}).jpg'.format(x - minx, y - miny)
            src = path_of_test_resource(os.sep.join(['imgs', relpath]))
            dest = os.path.join(tmpdir, relpath)
            copyfile(src, dest)
            result[x, y] = dest

        return result

    return func


@image_equivalence_test
@patch('stitch.core.load_tiles')
def test_stitch_inmemory(load):
    load.side_effect = _dummy_load()

    dummy_paths = {
        (x, y): 'http://dummy.com/({}_{}).png'.format(x, y)
        for x, y in cartesian_product(range(2, 5), range(3, 7))
    }

    actual = stitch(dummy_paths, 'RGB')
    expected = Image.open(path_of_test_resource('imgs/happypath_stitch_result.jpg'), 'r')
    return actual, expected


@image_equivalence_test
@patch('stitch.core.save_tiles')
def test_stitch_tempdir_intermediate(save):
    save.side_effect = _dummy_save()

    dummy_paths = {
        (x, y): 'http://dummy.com/({}_{}).png'.format(x, y)
        for x, y in cartesian_product(range(2, 5), range(3, 7))
    }

    actual = stitch(dummy_paths, 'RGB', tempfiles=True)
    expected = Image.open(path_of_test_resource('imgs/happypath_stitch_result.jpg'), 'r')
    return actual, expected


@image_equivalence_test
@patch('stitch.core.load_tiles')
def test_stitch_some_missing_tiles(load):
    load.side_effect = _dummy_load(exclude_tiles=((0,0), (1,2)))

    dummy_paths = {
        (x, y): 'http://dummy.com/({}_{}).png'.format(x, y)
        for x, y in cartesian_product(range(0, 3), range(0, 4))
    }

    actual = stitch(dummy_paths, 'RGB')
    expected = Image.open(path_of_test_resource('imgs/missingtiles_stitch_result.jpg'), 'r')
    return actual, expected


@image_equivalence_test
@patch('stitch.core.load_tiles')
def test_stitch_with_missing_column(load):
    exclude = [(0, i) for i in range(4)]
    load.side_effect = _dummy_load(exclude_tiles=exclude)

    dummy_paths = {
        (x, y): 'http://dummy.com/({}_{}).png'.format(x, y)
        for x, y in cartesian_product(range(0, 3), range(0, 4))
    }

    actual = stitch(dummy_paths, 'RGB')
    expected = Image.open(path_of_test_resource('imgs/missingcolumn_stitch_result.jpg'), 'r')
    return actual, expected


@patch('stitch.core.load_tiles')
def test_stitch_with_no_tiles(load):
    load.side_effect = lambda paths: dict()

    dummy_paths = {
        (x, y): 'http://dummy.com/({}_{}).png'.format(x, y)
        for x, y in cartesian_product(range(0, 3), range(0, 4))
    }

    with pytest.raises(StitchException):
        stitch(dummy_paths, 'RGB')
