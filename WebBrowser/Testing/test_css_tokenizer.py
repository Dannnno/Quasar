# -*- coding: utf-8 -*-

from nose.plugins.skip import SkipTest

from WebBrowser.parser.tokens.css_tokens import CSSTokenizer, StringToken, \
    BadStringToken, LiteralToken, WhitespaceToken


class TestLiteralTokens(object):

    @staticmethod
    def test_good_literal1():
        stream = CSSTokenizer("{")
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == '{'

    @staticmethod
    def test_good_literal2():
        stream = CSSTokenizer("}")
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == '}'

    @staticmethod
    def test_good_literal3():
        stream = CSSTokenizer('(')
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == '('

    @staticmethod
    def test_good_literal4():
        stream = CSSTokenizer(')')
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == ')'

    @staticmethod
    def test_good_literal5():
        stream = CSSTokenizer('[')
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == '['

    @staticmethod
    def test_good_literal6():
        stream = CSSTokenizer(']')
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == ']'

    @staticmethod
    def test_good_literal7():
        stream = CSSTokenizer(':')
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == ':'

    @staticmethod
    def test_good_literal8():
        stream = CSSTokenizer(';')
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == ';'

    @staticmethod
    def test_good_literal9():
        stream = CSSTokenizer(',')
        stream.tokenize_stream()
        literal_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(literal_token, LiteralToken)
        assert literal_token.value == ','


class TestWhitespaceToken(object):

    @staticmethod
    def test_good_whitespace1():
        stream = CSSTokenizer('\n')
        stream.tokenize_stream()
        whitespace_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(whitespace_token, WhitespaceToken)
        assert whitespace_token.value == ' '

    @staticmethod
    def test_good_whitespace2():
        stream = CSSTokenizer('\r')
        stream.tokenize_stream()
        whitespace_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(whitespace_token, WhitespaceToken)
        assert whitespace_token.value == ' '

    @staticmethod
    def test_good_whitespace3():
        stream = CSSTokenizer('\f')
        stream.tokenize_stream()
        whitespace_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(whitespace_token, WhitespaceToken)
        assert whitespace_token.value == ' '

    @staticmethod
    def test_good_whitespace4():
        stream = CSSTokenizer('\r\n')
        stream.tokenize_stream()
        whitespace_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(whitespace_token, WhitespaceToken)
        assert whitespace_token.value == ' '

    @staticmethod
    def test_good_whitespace5():
        stream = CSSTokenizer(' ')
        stream.tokenize_stream()
        whitespace_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(whitespace_token, WhitespaceToken)
        assert whitespace_token.value == ' '

    @staticmethod
    def test_good_whitespace6():
        stream = CSSTokenizer('\t')
        stream.tokenize_stream()
        whitespace_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(whitespace_token, WhitespaceToken)
        assert whitespace_token.value == ' '

    @staticmethod
    def test_good_whitespace7():
        stream = CSSTokenizer('    ')
        stream.tokenize_stream()
        whitespace_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(whitespace_token, WhitespaceToken)
        assert whitespace_token.value == ' '


class TestStringTokenizing(object):

    @staticmethod
    def test_good_string1():
        stream = CSSTokenizer("'I am a string'")
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert string_token.value == 'I am a string'

    @staticmethod
    def test_good_string2():
        stream = CSSTokenizer('"I am also a string"')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert string_token.value == 'I am also a string'

    @staticmethod
    def test_good_string_escaped_newline1():
        stream = CSSTokenizer('''"I have an\\\nokay newline"''')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert string_token.value == r'I have an\\nokay newline'

    @staticmethod
    def test_good_string_escaped_newline2():
        stream = CSSTokenizer('''"I have an\\\rokay newline"''')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert string_token.value == r'I have an\\nokay newline'

    @staticmethod
    def test_good_string_escaped_newline3():
        stream = CSSTokenizer('''"I have an\\\fokay newline"''')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert string_token.value == r'I have an\\nokay newline'

    @staticmethod
    def test_good_string_escaped_newline4():
        stream = CSSTokenizer('''"I have an\\\r\nokay newline"''')
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert not stream._stream
        assert isinstance(string_token, StringToken)
        assert string_token.value == r'I have an\\nokay newline'

    @staticmethod
    def test_bad_string1():
        # I need to have other parts working that handle non-string tokens to
        # pick up from the bad string
        raise SkipTest
        stream = CSSTokenizer('"Guess what I\n am?"')
        # Answer: Not a good string token
        stream.tokenize_stream()
        string_token = stream.consume_token()
        assert isinstance(string_token, BadStringToken)
        assert string_token.value == ''
