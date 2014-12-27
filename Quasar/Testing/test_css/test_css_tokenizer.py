# -*- coding: UTF-8 -*-
from collections import deque

from nose.plugins.skip import SkipTest

from Quasar.parser.tokens.css_tokens import CSSTokenizer, WhitespaceToken, \
    preprocessing, NumberToken, PercentageToken, DimensionToken


class TestPreprocessing(object):

    @staticmethod
    def test_replace_carriage_return_and_line_feed():
        assert preprocessing(u'\u000D\u000Fasdf') == u'\u000Aasdf'

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
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_name_start_letter():
        token_stream = CSSTokenizer('-H')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_name_start_non_ascii():
        token_stream = CSSTokenizer('-�')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_name_start_underscore():
        token_stream = CSSTokenizer('-_')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_escape():
        token_stream = CSSTokenizer('-\\l')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_hyphen_bad_escape():
        token_stream = CSSTokenizer('-\\\n')
        token_stream.consume_next_code_point()
        assert not token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_name_start_letter():
        token_stream = CSSTokenizer('H')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_name_start_non_ascii():
        token_stream = CSSTokenizer('�')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_name_start_underscore():
        token_stream = CSSTokenizer('_')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_escape():
        token_stream = CSSTokenizer('\\l')
        token_stream.consume_next_code_point()
        assert token_stream._starts_identifier()

    @staticmethod
    def test_starts_identifier_bad_escape():
        token_stream = CSSTokenizer('\\\n')
        token_stream.consume_next_code_point()
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
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345e9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("12345E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345E9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("12345e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345e+9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("12345E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345E+9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("12345e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '12345e-9'

    @staticmethod
    def test_unsigned_integer_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("12345E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.000012345
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
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345e9'

    @staticmethod
    def test_signed_negative_integer_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("-12345e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345e9'

    @staticmethod
    def test_signed_positive_integer_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("+12345E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345E9'

    @staticmethod
    def test_signed_negative_integer_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("-12345E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345E9'

    @staticmethod
    def test_positive_integer_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("+12345e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345e+9'

    @staticmethod
    def test_negative_integer_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("-12345e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345e+9'

    @staticmethod
    def test_positive_integer_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("+12345E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345E+9'

    @staticmethod
    def test_negative_integer_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("-12345E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -12345000000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345E+9'

    @staticmethod
    def test_positive_integer_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("+12345e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345e-9'

    @staticmethod
    def test_negative_integer_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("-12345e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -0.000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-12345e-9'

    @staticmethod
    def test_positive_integer_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("+12345E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+12345E-9'

    @staticmethod
    def test_negative_integer_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("-12345E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -0.000012345
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
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45e9'

    @staticmethod
    def test_unsigned_float_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("123.45E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45E9'

    @staticmethod
    def test_unsigned_float_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("123.45e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45e+9'

    @staticmethod
    def test_unsigned_float_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("123.45E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45E+9'

    @staticmethod
    def test_unsigned_float_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("123.45e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.00000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '123.45e-9'

    @staticmethod
    def test_unsigned_float_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("123.45E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.00000012345
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
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45e9'

    @staticmethod
    def test_signed_negative_float_scientific_notation_little_e_unsigned():
        token_stream = CSSTokenizer("-123.45e9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45e9'

    @staticmethod
    def test_signed_positive_float_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("+123.45E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45E9'

    @staticmethod
    def test_signed_negative_float_scientific_notation_big_e_unsigned():
        token_stream = CSSTokenizer("-123.45E9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45E9'

    @staticmethod
    def test_positive_float_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("+123.45e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45e+9'

    @staticmethod
    def test_negative_float_scientific_notation_little_e_signed_positive():
        token_stream = CSSTokenizer("-123.45e+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45e+9'

    @staticmethod
    def test_positive_float_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("+123.45E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45E+9'

    @staticmethod
    def test_negative_float_scientific_notation_big_e_signed_positive():
        token_stream = CSSTokenizer("-123.45E+9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -123450000000.0
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45E+9'

    @staticmethod
    def test_positive_float_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("+123.45e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.00000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '+123.45e-9'

    @staticmethod
    def test_negative_float_scientific_notation_little_e_signed_negative():
        token_stream = CSSTokenizer("-123.45e-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == -0.00000012345
        assert token_stream.tokens[0].type_ == 'number'
        assert token_stream.tokens[0].string == '-123.45e-9'

    @staticmethod
    def test_positive_float_scientific_notation_big_e_signed_negative():
        token_stream = CSSTokenizer("+123.45E-9")
        token_stream.tokenize_stream()
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], NumberToken)
        assert token_stream.tokens[0].value == 0.00000012345
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
    def test_consume_name_escape_tokens():
        token_stream = CSSTokenizer("\\a\\3\\9\\!")
        assert token_stream._consume_name() == 'a39!'
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
        assert token_stream.tokens[0].type_ is None
        assert token_stream.tokens[0].value == 12345
        assert token_stream.tokens[0].string == '12345'
        assert str(token_stream.tokens[0]) == '12345 %'


class TestDimensionToken(object):

    @staticmethod
    def test_consume_numeric_token_dimenstion1():
        token_stream = CSSTokenizer("12345meters")
        token_stream.consume_numeric_token()
        print token_stream._starts_identifier()
        print token_stream.stream
        assert not token_stream.stream
        assert isinstance(token_stream.tokens[0], DimensionToken)
        assert token_stream.tokens[0].type_ is 'integer'
        assert token_stream.tokens[0].value == 12345
        assert token_stream.tokens[0].string == '12345'
        assert token_stream.tokens[0].unit == 'meters'
        assert str(token_stream.tokens[0]) == '12345 meters'

