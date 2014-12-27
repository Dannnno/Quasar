from nose.plugins.skip import SkipTest

from Quasar.parser.tokens.css_tokens import LiteralToken, CSSTokenizer, \
    HashToken, WhitespaceToken


def test_small_css():
    css = """#gbar,#guser {
    font-size : 13px;
    padding-top : 1px !important;
}
"""
    raise SkipTest
    stream = CSSTokenizer(css)
    stream.tokenize_stream()
    assert isinstance(stream.tokens[0], HashToken)
    assert repr(stream.tokens[0]) == 'gbar'
    assert isinstance(stream.tokens[1], LiteralToken)
    assert repr(stream.tokens[1]) == ','
    assert isinstance(stream.tokens[2], HashToken)
    assert repr(stream.tokens[2]) == 'guser'
    assert isinstance(stream.tokens[3], LiteralToken)
    assert repr(stream.tokens[3]) == '{'
    assert isinstance(stream.tokens[4], None)
    assert repr(stream.tokens[4]) == 'font-size'
    assert isinstance(stream.tokens[5], LiteralToken)
    assert repr(stream.tokens[5]) == ':'
    assert isinstance(stream.tokens[6], None)
    assert repr(stream.tokens[6]) == '13px'
    assert isinstance(stream.tokens[7], LiteralToken)
    assert repr(stream.tokens[7]) == ';'
    assert isinstance(stream.tokens[8], None)
    assert repr(stream.tokens[8]) == 'padding-top'
    assert isinstance(stream.tokens[9], LiteralToken)
    assert repr(stream.tokens[9]) == ':'
    assert isinstance(stream.tokens[10], None)
    assert repr(stream.tokens[10]) == '1px'
    assert isinstance(stream.tokens[11], None)
    assert repr(stream.tokens[11]) == '!important'
    assert isinstance(stream.tokens[12], LiteralToken)
    assert repr(stream.tokens[12]) == ';'
    assert isinstance(stream.tokens[13], LiteralToken)
    assert repr(stream.tokens[13]) == '}'
