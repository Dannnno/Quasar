from nose.tools import assert_raises

from Quasar.parser.tokens.css_tokens import CSSTokenizer, HashToken, \
    WhitespaceToken, LiteralToken, DimensionToken, IdentToken, DelimToken


class TestSmallCSS1(object):

    @classmethod
    def setup_class(cls):
        cls.css = """#gbar,#guser {
    font-size : 13px;
    padding-top : 1px !important;
}"""
        cls.stream = CSSTokenizer(cls.css)
        cls.stream.tokenize_stream()
        cls.tokens = cls.stream.tokens

    def test_remaining_stream(self):
        assert not self.stream.stream

    def test_first_token(self):
        assert isinstance(self.tokens[0], HashToken)
        assert self.tokens[0].value == 'gbar'

    def test_second_token(self):
        assert isinstance(self.tokens[1], LiteralToken)
        assert self.tokens[1].value == ','

    def test_third_token(self):
        assert isinstance(self.tokens[2], HashToken)
        assert self.tokens[2].value == 'guser'

    def test_fourth_token(self):
        assert isinstance(self.tokens[3], WhitespaceToken)
        assert self.tokens[3].value == ' '

    def test_fifth_token(self):
        assert isinstance(self.tokens[4], LiteralToken)
        assert self.tokens[4].value == '{'

    def test_sixth_token(self):
        assert isinstance(self.tokens[5], WhitespaceToken)
        assert self.tokens[5].value == ' '

    def test_seventh_token(self):
        assert isinstance(self.tokens[6], IdentToken)
        assert self.tokens[6].value == 'font-size'

    def test_eighth_token(self):
        assert isinstance(self.tokens[7], WhitespaceToken)
        assert self.tokens[7].value == ' '

    def test_ninth_token(self):
        assert isinstance(self.tokens[8], LiteralToken)
        assert self.tokens[8].value == ':'

    def test_tenth_token(self):
        assert isinstance(self.tokens[9], WhitespaceToken)
        assert self.tokens[9].value == ' '

    def test_eleventh_token(self):
        assert isinstance(self.tokens[10], DimensionToken)
        assert self.tokens[10].string == '13'
        assert self.tokens[10].value == 13
        assert self.tokens[10].unit == 'px'
        assert self.tokens[10].type_ == 'integer'

    def test_twelfth_token(self):
        assert isinstance(self.tokens[11], LiteralToken)
        assert self.tokens[11].value == ';'

    def test_thirteenth_token(self):
        assert isinstance(self.tokens[12], WhitespaceToken)
        assert self.tokens[12].value == ' '

    def test_fourteenth_token(self):
        assert isinstance(self.tokens[13], IdentToken)
        assert self.tokens[13].value == 'padding-top'

    def test_fifteenth_token(self):
        assert isinstance(self.tokens[14], WhitespaceToken)
        assert self.tokens[14].value == ' '

    def test_sixteenth_token(self):
        assert isinstance(self.tokens[15], LiteralToken)
        assert self.tokens[15].value == ':'

    def test_seventeenth_token(self):
        assert isinstance(self.tokens[16], WhitespaceToken)
        assert self.tokens[16].value == ' '

    def test_eighteenth_token(self):
        assert isinstance(self.tokens[17], DimensionToken)
        assert self.tokens[17].value == 1
        assert self.tokens[17].string == '1'
        assert self.tokens[17].type_ == 'integer'
        assert self.tokens[17].unit == 'px'

    def test_nineteenth_token(self):
        assert isinstance(self.tokens[18], WhitespaceToken)
        assert self.tokens[18].value == ' '

    def test_twentieth_token(self):
        assert isinstance(self.tokens[19], DelimToken)
        assert self.tokens[19].value == '!'

    def test_twenty_first_token(self):
        assert isinstance(self.tokens[20], IdentToken)
        assert self.tokens[20].value == 'important'

    def test_twenty_second_token(self):
        assert isinstance(self.tokens[21], LiteralToken)
        assert self.tokens[21].value == ';'

    def test_twenty_third_token(self):
        assert isinstance(self.tokens[22], WhitespaceToken)
        assert self.tokens[22].value == ' '

    def test_twenty_fourth_token(self):
        assert isinstance(self.tokens[23], LiteralToken)
        assert self.tokens[23].value == '}'

    def test_no_more_tokens(self):
        assert_raises(IndexError, self.tokens.__getitem__, 24)
