#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the yatiml module.
"""
import pytest

from yatiml import yatiml


def test_without_test_object():
    assert False


class TestYatiml(object):
    @pytest.fixture
    def return_a_test_object(self):
        pass

    def test_yatiml(self, yatiml):
        assert False

    def test_with_error(self, yatiml):
        with pytest.raises(ValueError):
            pass
