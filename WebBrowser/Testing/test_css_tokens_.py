# -*- coding: utf-8 -*-
# Implemented as per http://dev.w3.org/csswg/css-syntax/#tokenizing-and-parsing
from nose.plugins.skip import SkipTest
from nose.tools import assert_raises
from WebBrowser.parser.tokens.css_tokens import CSSTokenizer, preprocessing, \
    WhitespaceToken, LiteralToken, StringToken, BadStringToken


class TestLiteralTokens(object):

    @staticmethod
    def test_good_literal1():
        css = LiteralToken(preprocessing("{"))
        css.tokenize()
        assert css.value == '{'
        assert css.match

    @staticmethod
    def test_good_literal2():
        css = LiteralToken(preprocessing("}"))
        css.tokenize()
        assert css.value == '}'
        assert css.match

    @staticmethod
    def test_good_literal3():
        css = LiteralToken(preprocessing("("))
        css.tokenize()
        assert css.value == '('
        assert css.match

    @staticmethod
    def test_good_literal4():
        css = LiteralToken(preprocessing(")"))
        css.tokenize()
        assert css.value == ')'
        assert css.match

    @staticmethod
    def test_good_literal5():
        css = LiteralToken(preprocessing("["))
        css.tokenize()
        assert css.value == '['
        assert css.match

    @staticmethod
    def test_good_literal6():
        css = LiteralToken(preprocessing("]"))
        css.tokenize()
        assert css.value == ']'
        assert css.match

    @staticmethod
    def test_good_literal7():
        css = LiteralToken(preprocessing(":"))
        css.tokenize()
        assert css.value == ':'
        assert css.match

    @staticmethod
    def test_good_literal8():
        css = LiteralToken(preprocessing(";"))
        css.tokenize()
        assert css.value == ';'
        assert css.match

    @staticmethod
    def test_good_literal9():
        css = LiteralToken(preprocessing(","))
        css.tokenize()
        assert css.value == ','
        assert css.match

    @staticmethod
    def test_bad_literal():
        assert_raises(ValueError, LiteralToken, (preprocessing("sdfaef\nasf")))


class TestWhitespaceToken(object):

    @staticmethod
    def test_good_whitespace1():
        css = WhitespaceToken(preprocessing("\n"))
        css.tokenize()
        assert css.value == ' '
        assert css.match

    @staticmethod
    def test_good_whitespace2():
        css = WhitespaceToken(preprocessing("\r"))
        css.tokenize()
        assert css.value == ' '
        assert css.match

    @staticmethod
    def test_good_whitespace3():
        css = WhitespaceToken(preprocessing("\f"))
        css.tokenize()
        assert css.value == ' '
        assert css.match

    @staticmethod
    def test_good_whitespace4():
        css = WhitespaceToken(preprocessing("\r\n"))
        css.tokenize()
        assert css.value == ' '
        assert css.match

    @staticmethod
    def test_good_whitespace5():
        css = WhitespaceToken(preprocessing(" "))
        css.tokenize()
        assert css.value == ' '
        assert css.match

    @staticmethod
    def test_good_whitespace6():
        css = WhitespaceToken(preprocessing("\t"))

        css.tokenize()
        assert css.value == ' '
        assert css.match

    @staticmethod
    def test_good_whitespace7():
        css = WhitespaceToken(preprocessing("    "))
        css.tokenize()
        assert css.value == ' '
        assert css.match

    @staticmethod
    def test_bad_whitespace():
        css = WhitespaceToken(preprocessing("sdfaef\nasdf"))
        css.tokenize()
        assert css.value is None
        assert not css.match


class TestStringTokens(object):

    @staticmethod
    def test_good_string1():
        stream = CSSTokenizer("'I am a string'")
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert str(string_token) == 'I am a string'

    @staticmethod
    def test_good_string2():
        stream = CSSTokenizer('"I am also a string"')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert str(string_token) == 'I am also a string'

    @staticmethod
    def test_good_string3():
        stream = CSSTokenizer('''"I have an \\nokay newline"''')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert str(string_token) == 'I am also a \\n string'

    @staticmethod
    def test_bad_string1():
        # I need to have other parts working that handle non-string tokens to
        # pick up from the bad string
        # raise SkipTest
        stream = CSSTokenizer('"Guess what I\n am?"')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert isinstance(string_token, BadStringToken)
        assert str(string_token) == ''