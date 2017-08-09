import os
import sys
from itertools import product as cartesian_product

import pytest
from PIL import Image

from stitch.core import stitch, StitchException, overlay, side_by_side
from stitch.tests._common import image_equivalence_test, path_of_test_resource, open_image

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


@patch('stitch.core.load_tiles')
def test_stitch_limit_number_of_tiles(load):
    load.side_effect = _dummy_load()

    too_many_tiles = {
        (x, y): 'http://dummy.com/({}_{}).png'.format(x, y)
        for x, y in cartesian_product(range(10), range(5))
    }

    with pytest.raises(StitchException):
        stitch(too_many_tiles, 'RGB')


@image_equivalence_test
def test_overlay_top_left():
    im = open_image('imgs/baseimg.jpg')
    wm = open_image('imgs/copyright-small.png')
    result = overlay(im, wm)
    expected = open_image('imgs/happypath_overlay_result.jpg')

    return result, expected


@image_equivalence_test
def test_overlay_bottom_right():
    im = open_image('imgs/baseimg.jpg')
    wm = open_image('imgs/copyright-small.png')
    result = overlay(im, wm, pos=(im.width - wm.width, im.height - wm.height))
    expected = open_image('imgs/bottomright_overlay_result.jpg')

    return result, expected


@image_equivalence_test
def test_sidebyside_right_img_larger():
    im1 = open_image('imgs/baseimg.jpg')
    im2 = open_image('imgs/anotherimg.jpg')
    result = side_by_side(im1, im2, 'RGB')
    expected = open_image('imgs/happypath_sidebyside_result.jpg')

    return result, expected


@image_equivalence_test
def test_sidebyside_left_img_smaller():
    im1 = open_image('imgs/anotherimg.jpg')
    im2 = open_image('imgs/baseimg.jpg')
    result = side_by_side(im1, im2, 'RGB')
    expected = open_image('imgs/smallerleft_sidebyside_result.jpg')

    return result, expected


@image_equivalence_test
def test_sidebyside_center_align():
    im1 = open_image('imgs/anotherimg.jpg')
    im2 = open_image('imgs/baseimg.jpg')
    result = side_by_side(im1, im2, 'RGB', valign='center')
    expected = open_image('imgs/valign_center_sidebyside_result.jpg')

    return result, expected


@image_equivalence_test
def test_sidebyside_top_align():
    im1 = open_image('imgs/anotherimg.jpg')
    im2 = open_image('imgs/baseimg.jpg')
    result = side_by_side(im1, im2, 'RGB', valign='top')
    expected = open_image('imgs/valign_top_sidebyside_result.jpg')

    return result, expected


def test_sidebyside_invalid_align():
    im1 = open_image('imgs/anotherimg.jpg')
    im2 = open_image('imgs/baseimg.jpg')
    with pytest.raises(ValueError):
        side_by_side(im1, im2, 'RGB', valign='invalid-argument')
