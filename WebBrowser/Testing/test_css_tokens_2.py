# -*- coding: utf-8 -*-
# Implemented as per http://dev.w3.org/csswg/css-syntax/#tokenizing-and-parsing
from nose.plugins.skip import SkipTest

from WebBrowser.parser.tokens.css_tokens import CSSTokenizer, preprocessing, WhitespaceToken


class TestWhitespaceToken(object):

    def test_good_whitespace1(self):
        input = WhitespaceToken(preprocessing("""\n"""))
        input.tokenize()
        assert input.value == ' '
        assert input.match

    def test_good_whitespace2(self):
        input = WhitespaceToken(preprocessing("""\r"""))
        input.tokenize()
        assert input.value == ' '
        assert input.match

    def test_good_whitespace3(self):
        input = WhitespaceToken(preprocessing("""\f"""))
        input.tokenize()
        assert input.value == ' '
        assert input.match

    def test_good_whitespace4(self):
        input = WhitespaceToken(preprocessing("""\r\n"""))
        input.tokenize()
        assert input.value == ' '
        assert input.match

    def test_good_whitespace5(self):
        input = WhitespaceToken(preprocessing(""" """))
        input.tokenize()
        assert input.value == ' '
        assert input.match

    def test_good_whitespace6(self):
        input = WhitespaceToken(preprocessing("""\t"""))
        input.tokenize()
        assert input.value == ' '
        assert input.match

    def test_good_whitespace7(self):
        input = WhitespaceToken(preprocessing("""    """))
        input.tokenize()
        assert input.value == ' '
        assert input.match

    def test_bad_whitespace(self):
        input = WhitespaceToken(preprocessing("""sdfaef\nasdf"""))
        input.tokenize()
        assert input.value is None
        assert not input.match

