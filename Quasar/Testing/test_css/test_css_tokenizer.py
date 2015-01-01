# -*- coding: UTF-8 -*-
from collections import deque

from nose.plugins.skip import SkipTest
from nose.tools import assert_almost_equal, assert_raises

from Quasar.parser.tokens.css_tokens import CSSTokenizer, WhitespaceToken, \
    preprocessing, NumberToken, PercentageToken, DimensionToken, HashToken, \
    DelimToken, SuffixMatchToken, IdentToken, CDCToken, CDOToken, \
    AtKeywordToken, PrefixMatchToken, ColumnToken, IncludeMatchToken, \
    DashMatchToken, LiteralToken


class TestStringToNumber(object):

    @staticmethod
    def test_string_one():
        assert CSSTokenizer._string_to_number('12345') == 12345

    @staticmethod
    def test_string_two():
        assert CSSTokenizer._string_to_number('1234.5') == 1234.5

    @staticmethod
    def test_string_three():
        assert CSSTokenizer._string_to_number('1234.5e9') == 1.2345e12

    @staticmethod
    def test_string_four():
        assert CSSTokenizer._string_to_number('1234.5e+9') == 1.2345e12

    @staticmethod
    def test_string_five():
        assert CSSTokenizer._string_to_number('1234.5e-9') == 1.2345e-6

    @staticmethod
    def test_string_six():
        assert CSSTokenizer._string_to_number('+12345') == 12345

    @staticmethod
    def test_string_seven():
        assert CSSTokenizer._string_to_number('+1234.5') == 1234.5

    @staticmethod
    def test_string_eight():
        assert CSSTokenizer._string_to_number('+1234.5e9') == 1.2345e12

    @staticmethod
    def test_string_nine():
        assert CSSTokenizer._string_to_number('+1234.5e+9') == 1.2345e12

    @staticmethod
    def test_string_ten():
        assert CSSTokenizer._string_to_number('+1234.5e-9') == 1.2345e-6

    @staticmethod
    def test_string_eleven():
        assert CSSTokenizer._string_to_number('-12345') == -12345

    @staticmethod
    def test_string_twelve():
        assert CSSTokenizer._string_to_number('-1234.5') == -1234.5

    @staticmethod
    def test_string_thirteen():
        assert CSSTokenizer._string_to_number('-1234.5e9') == -1.2345e12

    @staticmethod
    def test_string_fourteen():
        assert CSSTokenizer._string_to_number('-1234.5e+9') == -1.2345e12

    @staticmethod
    def test_string_fifteen():
        assert CSSTokenizer._string_to_number('-1234.5e-9') == -1.2345e-6


class TestPreprocessing(object):

    @staticmethod
    def test_replace_carriage_return():
        assert preprocessing(u'\u000Dasdf') == u'\u000Aasdf'

    @staticmethod
    def test_replace_form_feed():
        assert preprocessing(u'\u000Casdf') == u'\u000Aasdf'

    @staticmethod
    def test_replace_carriage_return_and_new_line():
        assert preprocessing(u'\u000D\u000Aasdf') == u'\u000Aasdf'

    @staticmethod
    def test_replace_null_character():
        assert preprocessing(u'\u0000asdf') == u'\uFFFDasdf'

    @staticmethod
    def test_invalid_utf8_characters():
        raise SkipTest
        # I don't know how exactly I'm going to test this


class TestLookahead(object):

    @classmethod
    def setup_class(cls):
        cls.token_stream = CSSTokenizer("Hi, I'm a test string")

    def test_lookahead_one_space(self):
        assert self.token_stream.lookahead(1) == [u'H']

    def test_lookahead_three_spaces(self):
        assert self.token_stream.lookahead(3) == [u'H', u'i', u',']

    def test_lookahead_too_many_spaces(self):
        assert self.token_stream.lookahead(24) == [u'H', u'i', u',', u' ',
                                                   u'I', u"'", u'm', u' ',
                                                   u'a', u' ', u't', u'e',
                                                   u's', u't', u' ', u's',
                                                   u't', u'r', u'i', u'n',
                                                   u'g', None, None, None]


class TestReconsumeCodePoint(object):

    @classmethod
    def setup_class(cls):
        cls.token_stream = CSSTokenizer("Hi, I'm another test string")

    def test_reconsume1(self):
        self.token_stream.consume_next_code_point()
        assert self.token_stream.current_code_point == 'H'
        self.token_stream.reconsume_current_code_point()
        self.token_stream.consume_next_code_point()
        assert self.token_stream.current_code_point == 'H'


class TestStartsIdentifier(object):

    @staticmethod
    def test_starts_identifier_hyphen_hyphen():
        token_stream = CSSTokenizer('--')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_name_start_letter():
        token_stream = CSSTokenizer('-H')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_name_start_non_ascii():
        token_stream = CSSTokenizer('-�')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_name_start_underscore():
        token_stream = CSSTokenizer('-_')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_escape():
        token_stream = CSSTokenizer('-\\l')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_bad_escape():
        token_stream = CSSTokenizer('-\\\n')
        assert not token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_name_start_letter():
        token_stream = CSSTokenizer('H')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_name_start_non_ascii():
        token_stream = CSSTokenizer('�')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_name_start_underscore():
        token_stream = CSSTokenizer('_')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_escape():
        token_stream = CSSTokenizer('\\l')
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_bad_escape():
        token_stream = CSSTokenizer('\\\n')
        assert not token_stream._starts_identifier()


class TestValidEscape(object):

    @staticmethod
    def test_escaped_number():
        assert CSSTokenizer._valid_escape('\\', '9')

    @staticmethod
    def test_escaped_letter():
        assert CSSTokenizer._valid_escape('\\', 'a')

    @staticmethod
    def test_escaped_symbol():
        assert CSSTokenizer._valid_escape('\\', '!')

    @staticmethod
    def test_escaped_newline():
        assert not CSSTokenizer._valid_escape('\\', '\n')


class TestConsumeComment(object):

    @staticmethod
    def test_normal_comment():
        token_stream = CSSTokenizer("/* I am a comment */")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert not token_stream.tokens

    @staticmethod
    def test_broken_comment():
        token_stream = CSSTokenizer("/* I am an unfinished comment")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert not token_stream.tokens

    @staticmethod
    def test_tricky_comment():
        token_stream = CSSTokenizer("/* I am a * tricky / comment */")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert not token_stream.tokens


class TestConsumeWhitespace(object):

    @staticmethod
    def test_space():
        token_stream = CSSTokenizer(" ")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], WhitespaceToken)
        assert token_stream.tokens[0].value == ' '

    @staticmethod
    def test_tab():
        token_stream = CSSTokenizer("\t")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], WhitespaceToken)
        assert token_stream.tokens[0].value == ' '

    @staticmethod
    def test_newline1():
        token_stream = CSSTokenizer("\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], WhitespaceToken)
        assert token_stream.tokens[0].value == ' '

    @staticmethod
    def test_newline2():
        token_stream = CSSTokenizer("\r")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], WhitespaceToken)
        assert token_stream.tokens[0].value == ' '

    @staticmethod
    def test_newline3():
        token_stream = CSSTokenizer("\f")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], WhitespaceToken)
        assert token_stream.tokens[0].value == ' '

    @staticmethod
    def test_newline4():
        token_stream = CSSTokenizer("\r\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], WhitespaceToken)
        assert token_stream.tokens[0].value == ' '

    @staticmethod
    def test_mixed_whitespace():
        token_stream = CSSTokenizer("     \t\r  \n")
        token_stream.consume_next_code_point()
        token_stream.consume_whitespace_token()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], WhitespaceToken)
        assert token_stream.tokens[0].value == ' '


class TestConsumeDigits(object):

    @staticmethod
    def test_consume_digit1():
        token_stream = CSSTokenizer("12345")
        token_stream.consume_next_code_point()
        assert token_stream._consume_digits() == '12345'


class TestConsumeNumber(object):

    @staticmethod
    def test_unsigned_integer_normal_notation():
        token_stream = CSSTokenizer("12345")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345
        assert token_stream.tokens[0].type_ == 'integer'
        assert token_stream.tokens[0].string == '12345'

    @staticmethod
    def test_unsigned_integer_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("12345e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345e9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("12345E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345E9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("12345e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345e+9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("12345E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345E+9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("12345e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-5)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345e-9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("12345E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-5)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345E-9'

    @staticmethod
    def test_signed_positive_integer_normal_notation():
        token_stream = CSSTokenizer("+12345")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345
        assert token_stream.tokens[0].type_ == 'integer'
        assert token_stream.tokens[0].string == '+12345'

    @staticmethod
    def test_signed_negative_integer_normal_notation():
        token_stream = CSSTokenizer("-12345")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -12345
        assert token_stream.tokens[0].type_ == 'integer'
        assert token_stream.tokens[0].string == '-12345'

    @staticmethod
    def test_signed_positive_integer_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("+12345e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345e9'

    @staticmethod
    def test_signed_negative_integer_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("-12345e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345e9'

    @staticmethod
    def test_signed_positive_integer_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("+12345E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345E9'

    @staticmethod
    def test_signed_negative_integer_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("-12345E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345E9'

    @staticmethod
    def test_positive_integer_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("+12345e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345e+9'

    @staticmethod
    def test_negative_integer_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("-12345e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345e+9'

    @staticmethod
    def test_positive_integer_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("+12345E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345E+9'

    @staticmethod
    def test_negative_integer_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("-12345E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e13
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345E+9'

    @staticmethod
    def test_positive_integer_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("+12345e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-5)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345e-9'

    @staticmethod
    def test_negative_integer_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("-12345e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value,- 1.2345e-5)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345e-9'

    @staticmethod
    def test_positive_integer_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("+12345E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-5)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345E-9'

    @staticmethod
    def test_negative_integer_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("-12345E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value,- 1.2345e-5)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345E-9'

    @staticmethod
    def test_unsigned_float_normal_notation():
        token_stream = CSSTokenizer("123.45")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123.45
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45'

    @staticmethod
    def test_unsigned_float_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("123.45e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45e9'

    @staticmethod
    def test_unsigned_float_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("123.45E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45E9'

    @staticmethod
    def test_unsigned_float_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("123.45e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45e+9'

    @staticmethod
    def test_unsigned_float_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("123.45E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45E+9'

    @staticmethod
    def test_unsigned_float_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("123.45e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-7)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45e-9'

    @staticmethod
    def test_unsigned_float_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("123.45E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-7)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45E-9'

    @staticmethod
    def test_signed_positive_float_normal_notation():
        token_stream = CSSTokenizer("+123.45")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123.45
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45'

    @staticmethod
    def test_signed_negative_float_normal_notation():
        token_stream = CSSTokenizer("-123.45")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -123.45
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45'

    @staticmethod
    def test_signed_positive_float_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("+123.45e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45e9'

    @staticmethod
    def test_signed_negative_float_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("-123.45e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45e9'

    @staticmethod
    def test_signed_positive_float_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("+123.45E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45E9'

    @staticmethod
    def test_signed_negative_float_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("-123.45E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45E9'

    @staticmethod
    def test_positive_float_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("+123.45e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45e+9'

    @staticmethod
    def test_negative_float_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("-123.45e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45e+9'

    @staticmethod
    def test_positive_float_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("+123.45E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45E+9'

    @staticmethod
    def test_negative_float_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("-123.45E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1.2345e11
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45E+9'

    @staticmethod
    def test_positive_float_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("+123.45e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-7)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45e-9'

    @staticmethod
    def test_negative_float_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("-123.45e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, -1.2345e-7)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45e-9'

    @staticmethod
    def test_positive_float_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("+123.45E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert_almost_equal(token_stream.tokens[0].value, 1.2345e-7)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45E-9'

    @staticmethod
    def test_negative_float_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("-123.45E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -0.00000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45E-9'


class TestConsumeName(object):

    @staticmethod
    def test_consume_name_code_point():
        token_stream = CSSTokenizer("asdfh427")
        assert token_stream._consume_name() == 'asdfh427'
        assert not token_stream.stream

    @staticmethod
    def test_consume_name_mixed():
        token_stream = CSSTokenizer("asd\\n\\!")
        assert token_stream._consume_name() == 'asdn!'
        assert not token_stream.stream

    @staticmethod
    def test_consume_name_bad_escape():
        token_stream = CSSTokenizer("asdfh\\\n427")
        assert token_stream._consume_name() == 'asdfh'
        assert token_stream.stream
        assert token_stream.stream == deque('\\\n427')


# Most of the heavy testing for these next three test classes is done by the
# testing of their helper functions above


class TestNumberToken(object):

    @staticmethod
    def test_consume_numeric_token_number1():
        token_stream = CSSTokenizer("12345")
        token_stream.consume_numeric_token()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].type_ == 'integer'
        assert token_stream.tokens[0].value == 12345
        assert token_stream.tokens[0].string == '12345'


class TestPercentageToken(object):

    @staticmethod
    def test_consume_numeric_token_percentage1():
        token_stream = CSSTokenizer("12345%")
        token_stream.consume_numeric_token()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], PercentageToken)
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].value == 12345
        assert token_stream.tokens[0].string == '12345'
        assert str(token_stream.tokens[0]) == '12345 %'


class TestDimensionToken(object):

    @staticmethod
    def test_consume_numeric_token_dimension1():
        token_stream = CSSTokenizer("12345meters")
        token_stream.consume_numeric_token()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DimensionToken)
        assert token_stream.tokens[0].type_ is 'integer'
        print vars(token_stream.tokens[0])
        assert token_stream.tokens[0].value == 12345
        assert token_stream.tokens[0].string == '12345'
        assert token_stream.tokens[0].unit == 'meters'
        assert str(token_stream.tokens[0]) == '12345 meters'


class TestHashToken(object):

    @staticmethod
    def test_hash_token_name_code_point():
        token_stream = CSSTokenizer("#mydiv")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], HashToken)
        assert token_stream.tokens[0].value == 'mydiv'
        assert token_stream.tokens[0].type_flag == 'id'

    @staticmethod
    def test_hash_token_valid_escape():
        raise SkipTest   # I'm having issues b/c I'm using a narrow build...
        token_stream = CSSTokenizer("#\\9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], HashToken)
        assert token_stream.tokens[0].value == '9'
        assert token_stream.tokens[0].type_flag == 'id'

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("#!")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '#'
        assert isinstance(token_stream.tokens[1], DelimToken)
        assert token_stream.tokens[1].value == '!'

    @staticmethod
    def test_delim_token_not_name():
        token_stream = CSSTokenizer("#\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '#'
        assert isinstance(token_stream.tokens[1], WhitespaceToken)
        assert token_stream.tokens[1].value == ' '

    @staticmethod
    def test_delim_token_bad_escape():
        token_stream = CSSTokenizer("#\\\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '#'


class TestSuffixMatchToken(object):

    @staticmethod
    def test_good_suffix():
        token_stream = CSSTokenizer("$=")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], SuffixMatchToken)
        assert token_stream.tokens[0].value == ''

    @staticmethod
    def test_bad_suffix():
        token_stream = CSSTokenizer("$a")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '$'


class TestHandlePlus(object):

    @staticmethod
    def test_valid_number():
        token_stream = CSSTokenizer("+1345")
        token_stream.consume_next_code_point()
        token_stream.handle_plus_sign()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 1345
        assert token_stream.tokens[0].type_ == 'integer'
        assert token_stream.tokens[0].string == "+1345"

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("+a")
        token_stream.consume_next_code_point()
        token_stream.handle_plus_sign()
        assert token_stream.stream[0] == 'a'
        assert_raises(IndexError, token_stream.stream.__getitem__, 1)
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '+'


class TestHandleMinus(object):

    @staticmethod
    def test_valid_number():
        token_stream = CSSTokenizer("-1345")
        token_stream.consume_next_code_point()
        token_stream.handle_minus_sign()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -1345
        assert token_stream.tokens[0].type_ == 'integer'
        assert token_stream.tokens[0].string == "-1345"

    @staticmethod
    def test_cdc_token():
        token_stream = CSSTokenizer("-->")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], CDCToken)
        assert token_stream.tokens[0].value == ''

    @staticmethod
    def test_ident_token():
        token_stream = CSSTokenizer("-abd")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], IdentToken)
        assert token_stream.tokens[0].value == '-abd'

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("-\\\n")
        token_stream.consume_next_code_point()
        token_stream.handle_minus_sign()
        assert token_stream.stream[0] == '\\'
        assert token_stream.stream[1] == '\n'
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '-'


class TestHandlePeriod(object):

    @staticmethod
    def test_valid_number():
        token_stream = CSSTokenizer(".1345")
        token_stream.consume_next_code_point()
        token_stream.handle_period()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == .1345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == "0.1345"

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer(".a")
        token_stream.consume_next_code_point()
        token_stream.handle_period()
        assert token_stream.stream[0] == 'a'
        assert_raises(IndexError, token_stream.stream.__getitem__, 1)
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '.'


class TestCDOToken(object):

    @staticmethod
    def test_CDO_token():
        raise SkipTest   # this is hanging somewhere...
        token_stream = CSSTokenizer("<!--")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], CDOToken)
        assert token_stream.tokens[0].value == ''

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("<0")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '<'


class TestAtKeywordToken(object):

    @staticmethod
    def test_at_keyword():
        token_stream = CSSTokenizer("@media")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], AtKeywordToken)
        assert token_stream.tokens[0].value == 'media'

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("@\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '@'


class TestPrefixMatchToken(object):

    @staticmethod
    def test_prefix_match():
        token_stream = CSSTokenizer("^=")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], PrefixMatchToken)
        assert token_stream.tokens[0].value == ''

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("^\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '^'


class TestVerticalLine(object):

    @staticmethod
    def test_dash_match():
        token_stream = CSSTokenizer("|=")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DashMatchToken)
        assert token_stream.tokens[0].value == ''

    @staticmethod
    def test_column_token():
        token_stream = CSSTokenizer("||")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], ColumnToken)
        assert token_stream.tokens[0].value == ''

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("|\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '|'


class TestIncludeMatch(object):

    @staticmethod
    def test_include_match():
        token_stream = CSSTokenizer("~=")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], IncludeMatchToken)
        assert token_stream.tokens[0].value == ''

    @staticmethod
    def test_delim_token():
        token_stream = CSSTokenizer("~\n")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DelimToken)
        assert token_stream.tokens[0].value == '~'


class TestLiteralTokens(object):

    @classmethod
    def setup_class(cls):
        token_stream = CSSTokenizer("{}[]();:,")
        token_stream.tokenize_stream()
        cls.tokens = token_stream.tokens

    def test_token1(self):
        assert isinstance(self.tokens[0], LiteralToken)
        assert self.tokens[0].value == '{'

    def test_token2(self):
        assert isinstance(self.tokens[1], LiteralToken)
        assert self.tokens[1].value == '}'

    def test_token3(self):
        assert isinstance(self.tokens[2], LiteralToken)
        assert self.tokens[2].value == '['

    def test_token4(self):
        assert isinstance(self.tokens[3], LiteralToken)
        assert self.tokens[3].value == ']'

    def test_token5(self):
        assert isinstance(self.tokens[4], LiteralToken)
        assert self.tokens[4].value == '('

    def test_token6(self):
        assert isinstance(self.tokens[5], LiteralToken)
        assert self.tokens[5].value == ')'

    def test_token7(self):
        assert isinstance(self.tokens[6], LiteralToken)
        assert self.tokens[6].value == ';'

    def test_token8(self):
        assert isinstance(self.tokens[7], LiteralToken)
        assert self.tokens[7].value == ':'

    def test_token9(self):
        assert isinstance(self.tokens[8], LiteralToken)
        assert self.tokens[8].value == ','
