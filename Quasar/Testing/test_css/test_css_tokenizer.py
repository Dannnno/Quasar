# -*- coding: UTF-8 -*-

from nose.plugins.skip import SkipTest

from Quasar.parser.tokens.css_tokens import CSSTokenizer


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