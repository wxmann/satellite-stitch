from datetime import datetime

import pytest
from PIL import ImageFilter

from stitch.postprocess import PostProcessor, CIRAPostProcessor, NICTPostProcessor
from stitch.tests._common import open_image, image_equivalence_test


@image_equivalence_test
def test_crop_relative():
    im = PostProcessor(open_image('imgs/baseimg.jpg'), datetime.utcnow())
    im.crop_relative(0.5, 0.25, 1.0, 0.9)
    return im.result(), open_image('imgs/baseimg_cropped.jpg')


def test_crop_relative_improper_params():
    im = PostProcessor(open_image('imgs/baseimg.jpg'), datetime.utcnow())
    with pytest.raises(ValueError):
        im.crop_relative(0.5, 0.25, 1.25, 0.9)


def test_minimize():
    im = PostProcessor(open_image('imgs/baseimg.jpg'), datetime.utcnow())
    im.minimize(500, 500)

    result = im.result()
    assert result.width == 500
    assert result.height == int(im.original.height * 500 / im.original.width)


@image_equivalence_test
def test_add_timestamp_label_default_params():
    im = PostProcessor(open_image('imgs/baseimg.jpg'), datetime(2017, 8, 6, 0, 0))
    im.timestamp_label()
    return im.result(), open_image('imgs/baseimg_w_timestamp.jpg')


@image_equivalence_test
def test_add_timestamp_label_custom_params():
    im = PostProcessor(open_image('imgs/baseimg.jpg'), datetime(2017, 8, 6, 0, 0))
    im.timestamp_label(padding=0.2, breadth=0.5)
    return im.result(), open_image('imgs/baseimg_w_timestamp_custom.jpg')


def test_add_timestamp_invalid_params():
    im = PostProcessor(open_image('imgs/baseimg.jpg'), datetime(2017, 8, 6, 0, 0))
    with pytest.raises(ValueError):
        im.timestamp_label(padding=0.5, breadth=1.0)


@image_equivalence_test
def test_add_sharpen_filter():
    im = PostProcessor(open_image('imgs/baseimg.jpg'), datetime.utcnow())
    im.apply_filter(ImageFilter.SHARPEN)
    return im.result(), open_image('imgs/baseimg_sharpened.jpg')


@image_equivalence_test
def test_add_cira_rammb_logo():
    im = CIRAPostProcessor(open_image('imgs/baseimg.jpg'), datetime.utcnow())
    im.logo()
    return im.result(), open_image('imgs/baseimg_ciralogo.jpg')


@image_equivalence_test
def test_add_cira_rammb_logo_big():
    im = CIRAPostProcessor(open_image('imgs/baseimg.jpg'), datetime.utcnow())
    im.logo(breadth=0.5)
    return im.result(), open_image('imgs/baseimg_ciralogo_big.jpg')


@image_equivalence_test
def test_add_nict_logo():
    im = NICTPostProcessor(open_image('imgs/baseimg.jpg'), datetime.utcnow())
    im.logo()
    return im.result(), open_image('imgs/baseimg_nictlogo.jpg')


@image_equivalence_test
def test_multiple_edits():
    im = NICTPostProcessor(open_image('imgs/baseimg.jpg'), datetime(2017, 8, 6, 0, 0))
    im.crop_relative(0.5, 0.25, 1.0, 0.9)
    im.apply_filter(ImageFilter.SHARPEN)
    im.timestamp_label()
    im.logo()
    return im.result(), open_image('imgs/baseimg_multiple_edits.jpg')