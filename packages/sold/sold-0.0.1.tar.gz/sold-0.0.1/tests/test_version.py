"""
Test that the version number exists and is valid.
"""

import packaging.version

import sold


def test_version_is_str():
    assert type(sold.__version__) is str


def test_version_is_valid():
    assert type(packaging.version.parse(sold.__version__)) is packaging.version.Version
