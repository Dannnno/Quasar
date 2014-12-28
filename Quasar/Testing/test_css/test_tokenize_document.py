from nose.plugins.skip import SkipTest

from Quasar.parser.tokens.css_tokens import CSSTokenizer


def test_small_css_1():
    css = """#gbar,#guser {
    font-size : 13px;
    padding-top : 1px !important;
}
    """
    raise SkipTest   # I haven't written it all yet
    stream = CSSTokenizer(css)
    stream.tokenize_stream()
    for token in stream.tokens:
        print token, type(token)
    assert not stream.stream
    assert False