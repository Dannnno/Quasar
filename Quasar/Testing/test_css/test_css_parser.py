from nose.plugins.skip import SkipTest

from Quasar.parser.tokens.css_tokens import CSSTokenizer
from Quasar.parser.ast.css_ast import ASTBuilderCSS


class TestParseStylesheet(object):

    pass


class TestParseCSSGrammar(object):

    pass


class TestParseListOfRules(object):

    pass


class TestParseRule(object):

    pass


class TestParseListOfDeclarations(object):

    pass


class TestParseDeclaration(object):

    pass


class TestParseListOfComponentValues(object):

    pass


class TestParseComponentValue(object):

    pass


class TestConsumeWhitespace(object):

    pass


class TestConsumeRulesList(object):

    pass


class TestConsumeAtRule(object):

    pass


class TestConsumeQualifiedRule(object):

    pass


class TestConsumeDeclarationsList(object):

    pass


class TestConsumeDeclaration(object):

    pass


class TestConsumeComponentValue(object):

    pass


class TestConsumeSimpleBlock(object):

    pass


class TestConsumeFunction(object):

    @staticmethod
    def test_consume_function1():
        raise SkipTest
        css = "myfunction(color : #aabbcc)"
        tokenizer = CSSTokenizer(css)
        tokenizer.tokenize_stream()
        tokens = tokenizer.tokens
        builder = ASTBuilderCSS(tokens)
        builder.consume_next_token()
        func = builder.consume_function()
        print func, vars(func)
        for token in tokens:
            print token, type(token)
        assert False
