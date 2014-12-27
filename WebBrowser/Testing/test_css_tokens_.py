# -*- coding: utf-8 -*-
# Implemented as per http://dev.w3.org/csswg/css-syntax/#tokenizing-and-parsing
from nose.plugins.skip import SkipTest
from nose.tools import assert_raises

from WebBrowser.parser.tokens.css_tokens import preprocessing, StringToken, \
    WhitespaceToken, LiteralToken, BadStringToken, string_chooser, \
    CSSTokenizer, HashToken, delim_token_chooser, DelimToken


class TestLiteralTokens(object):

    @staticmethod
    def test_good_literal1():
        css = LiteralToken(preprocessing("{"))
        css.tokenize()
        assert css.value == r'{'
        assert css.match

    @staticmethod
    def test_good_literal2():
        css = LiteralToken(preprocessing("}"))
        css.tokenize()
        assert css.value == r'}'
        assert css.match

    @staticmethod
    def test_good_literal3():
        css = LiteralToken(preprocessing("("))
        css.tokenize()
        assert css.value == r'('
        assert css.match

    @staticmethod
    def test_good_literal4():
        css = LiteralToken(preprocessing(")"))
        css.tokenize()
        assert css.value == r')'
        assert css.match

    @staticmethod
    def test_good_literal5():
        css = LiteralToken(preprocessing("["))
        css.tokenize()
        assert css.value == r'['
        assert css.match

    @staticmethod
    def test_good_literal6():
        css = LiteralToken(preprocessing("]"))
        css.tokenize()
        assert css.value == r']'
        assert css.match

    @staticmethod
    def test_good_literal7():
        css = LiteralToken(preprocessing(":"))
        css.tokenize()
        assert css.value == r':'
        assert css.match

    @staticmethod
    def test_good_literal8():
        css = LiteralToken(preprocessing(";"))
        css.tokenize()
        assert css.value == r';'
        assert css.match

    @staticmethod
    def test_good_literal9():
        css = LiteralToken(preprocessing(","))
        css.tokenize()
        assert css.value == r','
        assert css.match

    @staticmethod
    def test_bad_literal():
        assert_raises(ValueError, LiteralToken, (preprocessing("sdfaef\nasf")))


class TestWhitespaceToken(object):

    @staticmethod
    def test_good_whitespace1():
        css = WhitespaceToken(preprocessing("\n"))
        css.tokenize()
        assert css.value == r' '
        assert css.match

    @staticmethod
    def test_good_whitespace2():
        css = WhitespaceToken(preprocessing("\r"))
        css.tokenize()
        assert css.value == r' '
        assert css.match

    @staticmethod
    def test_good_whitespace3():
        css = WhitespaceToken(preprocessing("\f"))
        css.tokenize()
        assert css.value == r' '
        assert css.match

    @staticmethod
    def test_good_whitespace4():
        css = WhitespaceToken(preprocessing("\r\n"))
        css.tokenize()
        assert css.value == r' '
        assert css.match

    @staticmethod
    def test_good_whitespace5():
        css = WhitespaceToken(preprocessing(" "))
        css.tokenize()
        assert css.value == r' '
        assert css.match

    @staticmethod
    def test_good_whitespace6():
        css = WhitespaceToken(preprocessing("\t"))
        css.tokenize()
        assert css.value == r' '
        assert css.match

    @staticmethod
    def test_good_whitespace7():
        css = WhitespaceToken(preprocessing("    "))
        css.tokenize()
        assert css.value == r' '
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
        css = string_chooser('"', CSSTokenizer('I am a string"'))
        assert isinstance(css, StringToken)
        assert css.value == r"I am a string"

    @staticmethod
    def test_good_string2():
        css = string_chooser("'", CSSTokenizer("I am also a string'"))
        assert isinstance(css, StringToken)
        assert css.value == r"I am also a string"

    @staticmethod
    def test_good_string_escaped_newline1():
        css = string_chooser("'", CSSTokenizer("I have an\\\nokay newline'"))
        assert isinstance(css, StringToken)
        assert css.value == r'I have an\\nokay newline'

    @staticmethod
    def test_good_string_escaped_newline2():
        css = string_chooser('"', CSSTokenizer('I have an\\\rokay newline"'))
        assert isinstance(css, StringToken)
        assert css.value == r'I have an\\nokay newline'

    @staticmethod
    def test_good_string_escaped_newline3():
        css = string_chooser("'", CSSTokenizer("I have an\\\fokay newline'"))
        assert isinstance(css, StringToken)
        assert css.value == r'I have an\\nokay newline'

    @staticmethod
    def test_good_string_escaped_newline4():
        css = string_chooser('"', CSSTokenizer('I have an\\\r\nokay newline"'))
        assert isinstance(css, StringToken)
        assert css.value == r'I have an\\nokay newline'

    @staticmethod
    def test_bad_string1():
        css = string_chooser('"', CSSTokenizer('Guess what I\n am?"'))
        assert isinstance(css, BadStringToken)
        assert css.value == r''


class TestHashToken(object):

    @staticmethod
    def test_hash_startswith_name_code_point_letter():
        css = delim_token_chooser('#', CSSTokenizer('HashIDToken'))
        assert isinstance(css, HashToken)
        assert css.value == r"HashIDToken"
        #assert css.type_ == 'id'

    @staticmethod
    def test_hash_startswith_name_code_point_number():
        css = delim_token_chooser("#", CSSTokenizer("9wefasd"))
        assert isinstance(css, HashToken)
        assert css.value == r"9wefasd"
        #assert css.type_ == 'id'

    @staticmethod
    def test_hash_startswith_name_code_point_underscore():
        css = delim_token_chooser("#", CSSTokenizer("_sdf4"))
        assert isinstance(css, HashToken)
        assert css.value == r'_sdf4'
        #assert css.type_ == 'id'

    @staticmethod
    def test_hash_startswith_name_code_point_hyphen_name_start():
        css = delim_token_chooser('#', CSSTokenizer('-dds'))
        assert isinstance(css, HashToken)
        assert css.value == r'-dds'
        #assert css.type_ == 'id'

    @staticmethod
    def test_hash_startswith_name_code_point_hyphen_hyphen():
        css = delim_token_chooser('#', CSSTokenizer('--asdf'))
        assert isinstance(css, HashToken)
        assert css.value == r'--asdf'
        #assert css.type_ == 'id'

    @staticmethod
    def test_hash_startswith_name_code_point_hyphen_good_escape():
        raise SkipTest
        css = delim_token_chooser('#', CSSTokenizer('-\\9'))
        assert isinstance(css, HashToken)
        assert css.value == r'-\\9'
        #assert css.type_ == 'id'

    @staticmethod
    def test_hash_startswith_name_code_point_hyphen_bad_escape():
        raise SkipTest
        css = delim_token_chooser('#', CSSTokenizer('-\\\n'))
        assert isinstance(css, HashToken)
        assert css.value == r'-\\\n'
        assert css.type_ == 'unrestricted'

    @staticmethod
    def test_hash_startswith_name_code_point_non_ascii():
        raise SkipTest
        css = delim_token_chooser("#", CSSTokenizer(u"\uFFFFads"))
        assert isinstance(css, HashToken)
        assert css.value == r'\uFFFFads'
        #assert css.type_ == 'id'

    @staticmethod
    def test_hash_startswith_name_code_point_good_escape():
        raise SkipTest
        css = delim_token_chooser('#', CSSTokenizer('\\3'))
        assert isinstance(css, HashToken)
        assert css.value == r'\\3'
        # assert css.type_ == 'id'

    @staticmethod
    def test_hash_actually_delim():
        raise SkipTest
        css = delim_token_chooser('#', CSSTokenizer('|'))
        assert isinstance(css, DelimToken)
        assert css.value == '#'

    @staticmethod
    def test_hash_delim_bad_escape():
        raise SkipTest
        css = delim_token_chooser('#', CSSTokenizer('\\\n'))
        assert isinstance(css, DelimToken)
        assert css.value == '#'
