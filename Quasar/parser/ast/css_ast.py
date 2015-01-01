# -*- coding: UTF-8 -*-
from Quasar.parser.ast import ASTNode
from Quasar.parser.tokens.css_tokens import CSSTokenizer, WhitespaceToken, \
    AtKeywordToken, IdentToken, LiteralToken
from Quasar.exceptions.parse_exceptions import CSSSyntaxError


class CSSNode(ASTNode):

    def __init__(self, token, parent, children):
        super(CSSNode, self).__init__(token, parent, children)


class AtRule(CSSNode):

    pass


class QualifiedRule(CSSNode):

    pass


class Declaration(CSSNode):

    pass


class ComponentValue(CSSNode):

    pass


class PreservedToken(CSSNode):

    pass


class Function(CSSNode):

    pass


class SimpleBlock(CSSNode):

    pass


class Stylesheet(object):

    pass


class ASTBuilderCSS(object):
    EOF = None

    _stream = None
    _tree = None
    _current = None
    _next = None

    @property
    def css_token_stream(self):
        return self._stream

    @css_token_stream.setter
    def css_token_stream(self, new_stream):
        self._stream = new_stream

    @property
    def css_abstract_syntax_tree(self):
        return self._tree

    @css_abstract_syntax_tree.setter
    def css_abstract_syntax_tree(self, new_tree):
        self._tree = new_tree

    @property
    def current_token(self):
        return self._current

    @current_token.setter
    def current_token(self, new_token):
        self._current = new_token

    @property
    def next_token(self):
        return self._next

    @next_token.setter
    def next_token(self, stream):
        try:
            self._next = self.css_token_stream[0]
        except IndexError:
            self._next = self.EOF

    def consume_next_token(self):
        if self.next_token is not self.EOF:
            self.current_token = self.css_token_stream.popleft()
            self.next_token = self.css_token_stream
        else:
            raise StopIteration

    def lookahead(self, n=1):
        peek = []
        for i in range(n):
            try:
                peek.append(self.css_token_stream[i])
            except IndexError:
                peek.append(self.EOF)
        return peek

    @classmethod
    def from_file_like_object(cls, file_):
        try:
            return cls.from_string(file_.read())
        except ValueError:
            try:
                with open(file_, 'r') as f:
                    return cls.from_string(f.read())
            except ValueError:
                raise TypeError("Must be passed an open file-like object")

    @classmethod
    def from_string(cls, string):
        tokenized_css = CSSTokenizer(string)
        tokenized_css.tokenize_stream()
        return ASTBuilderCSS(tokenized_css.tokens)

    def __init__(self, token_stream):
        self.css_token_stream = token_stream
        self.css_abstract_syntax_tree = []

    def parse_grammar(self, input_to_parse, grammar_rule):
        result = self.parse_component_values_list(input_to_parse)
        match = self.match_grammar_rule(grammar_rule, result)
        if match:
            return match
        else:
            return False

    def parse_stylesheet(self):
        """Intended to be the normal entry point"""
        rules = self.consume_rules_list(self.css_token_stream,
                                        top_level_flag=True)
        return Stylesheet(rules)

    def parse_rules_list(self, stream):
        """Intended for the content of at-rules such as '@media'.  Handles
        CDC and CDO tokens differently from `parse_stylesheet`.
        """
        return self.consume_rules_list(stream, top_level_flag=False)


    def parse_rule(self):
        """Intended for use by the CSSStyleSheet#insertRule method, and similar
        functions which might exist, which parse text into a single rule.
        """
        self._consume_whitespace_token()
        if self.next_token is self.EOF:
            raise CSSSyntaxError("Unexpected EOF while parsing a rule.")
        elif isinstance(self.next_token, AtKeywordToken):
            rule = self.consume_at_rule()
        else:
            rule = self.consume_qualified_rule()
            if not rule:
                raise CSSSyntaxError("Invalid qualified rule.")
        self._consume_whitespace_token()
        if self.next_token is self.EOF:
            return rule
        else:
            raise CSSSyntaxError(
                "Expected EOF, found {}".format(type(self.next_token)))

    def parse_declarations_list(self):
        """For the contents of a style attribute, which parses text into the
        contents of a single style rule.
        """
        return self.consume_declarations_list()

    def parse_declaration(self):
        """Used in @supports conditions. http://www.w3.org/TR/css3-conditional/
        """
        self._consume_whitespace_token()
        if not isinstance(self.next_token, IdentToken):
            raise CSSSyntaxError(
                "Expected Ident Token, found {}".format(type(self.next_token)))
        declaration = self.consume_declaration()
        if not declaration:
            raise CSSSyntaxError("Expected a declaration, found nothing")
        return declaration

    def parse_component_values_list(self):
        component_value_list = []
        while self.next_token is not self.EOF:
            component_value = self.consume_component_value()
            if component_value is self.EOF:
                break
            else:
                component_value_list.append(component_value)
        return component_value_list

    def parse_csv_component_values_list(self):
        list_of_cvls = []
        while self.next_token is not self.EOF:
            inner_list = []
            while (not isinstance(self.next_token, LiteralToken) and
                   self.next_token.value == ','):
                inner_list.append(self.consume_component_value())
            list_of_cvls.append(inner_list)
        return list_of_cvls

    def parse_component_value(self):
        """For things that need to consume a single value, like the parsing
        rules for attr().
        """
        self._consume_whitespace_token()
        if self.next_token is self.EOF:
            raise CSSSyntaxError(
                "Unexpected EOF while parsing component value")
        component_value = self.consume_component_value()
        self._consume_whitespace_token()
        if self.next_token is self.EOF:
            return component_value
        else:
            raise CSSSyntaxError(
                "Expected EOF, found {}".format(type(self.next_token)))

    def _consume_whitespace_token(self):
        while isinstance(self.next_token, WhitespaceToken):
            self.consume_next_token()

    def consume_rules_list(self):
        """For the contents of presentational attributes, which parse text into
        a single declaration's value, or for parsing a stand-alone selector
        [1]_ or list of Media Queries [2]_, as in Selectors API [3]_ or the
        media HTML attribute.
        .. [1] http://www.w3.org/TR/2011/REC-css3-selectors-20110929/
        .. [2] http://www.w3.org/TR/2012/REC-css3-mediaqueries-20120619/
        .. [3] http://www.w3.org/TR/selectors-api/
        """
        pass

    def consume_at_rule(self):
        pass

    def consume_qualified_rule(self):
        pass

    def consume_declarations_list(self):
        pass

    def consume_declaration(self):
        pass

    def consume_component_value(self):
        pass

    def consume_simple_block(self):
        pass

    def consume_function(self):
        pass