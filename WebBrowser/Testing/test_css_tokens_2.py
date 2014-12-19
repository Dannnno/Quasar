# -*- coding: utf-8 -*-
# Implemented as per http://dev.w3.org/csswg/css-syntax/#tokenizing-and-parsing
from nose.plugins.skip import SkipTest
from nose.tools import assert_raises

from WebBrowser.parser.tokens.css_tokens import CSSTokenizer, preprocessing, WhitespaceToken, LiteralToken


class TestLiteralTokens(object):

    def test_good_literal1(self):
        input = LiteralToken(preprocessing("{"))
        input.tokenize()
        assert input.value == '{'
        assert input.match

    def test_good_literal2(self):
        input = LiteralToken(preprocessing("}"))
        input.tokenize()
        assert input.value == '}'
        assert input.match

    def test_good_literal3(self):
        input = LiteralToken(preprocessing("("))
        input.tokenize()
        assert input.value == '('
        assert input.match

    def test_good_literal4(self):
        input = LiteralToken(preprocessing(")"))
        input.tokenize()
        assert input.value == ')'
        assert input.match

    def test_good_literal5(self):
        input = LiteralToken(preprocessing("["))
        input.tokenize()
        assert input.value == '['
        assert input.match

    def test_good_literal6(self):
        input = LiteralToken(preprocessing("]"))
        input.tokenize()
        assert input.value == ']'
        assert input.match

    def test_good_literal7(self):
        input = LiteralToken(preprocessing(":"))
        input.tokenize()
        assert input.value == ':'
        assert input.match

    def test_good_literal8(self):
        input = LiteralToken(preprocessing(";"))
        input.tokenize()
        assert input.value == ';'
        assert input.match

    def test_good_literal9(self):
        input = LiteralToken(preprocessing(","))
        input.tokenize()
        assert input.value == ','
        assert input.match

    def test_bad_literal(self):
        assert_raises(ValueError, LiteralToken, (preprocessing("sdfaef\nasdf")))


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

