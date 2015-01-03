# -*- coding: UTF-8 -*-

from collections import deque

from Quasar.parser.tokens.css_tokens import CSSTokenizer, WhitespaceToken, \
    AtKeywordToken, IdentToken, LiteralToken, CDCToken, CDOToken, DelimToken, \
    FunctionToken
from Quasar.exceptions.parse_exceptions import CSSSyntaxError


class CSSNode(object): pass


class AtRule(CSSNode):

    def __init__(self, name, prelude, component_values):
        self.name = name
        self.prelude = prelude
        self.values = component_values


class QualifiedRule(CSSNode):

    def __init__(self, prelude, component_values):
        self.prelude = prelude
        self.values = component_values


class Declaration(CSSNode):

    def __init__(self, name, component_value):
        self.name = name
        self.value = component_value


class ComponentValue(CSSNode):

    def __init__(self, value):
        self.component = value


class PreservedToken(CSSNode):

    pass


class Function(CSSNode):

    def __init__(self, name, component_values):
        self.name = name
        self.values = component_values


class SimpleBlock(CSSNode):

    def __init__(self, associated_token, component_values):
        self.token = associated_token
        self.values = component_values


class Stylesheet(object):

    pass


class ASTBuilderCSS(object):
    EOF = None

    _stream = None
    _current = None
    _next = None

    @property
    def css_token_stream(self):
        return self._stream

    @css_token_stream.setter
    def css_token_stream(self, new_stream):
        self._stream = new_stream

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
            self._next = stream[0]
        except IndexError:
            self._next = self.EOF

    def consume_next_token(self):
        if self.css_token_stream:
            self.current_token = self.css_token_stream.popleft()
            self.next_token = self.css_token_stream

    def reconsume_current_token(self):
        self.css_token_stream.appendleft(self.current_token)
        self.next_token = self.css_token_stream
        self.current_token = None

    def lookahead(self, n=1):
        peek = []
        for i in range(n):
            try:
                peek.append(self.css_token_stream[i])
            except IndexError:
                peek.append(self.EOF)
        return peek

    @classmethod
    def from_file(cls, file_):
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

    def parse_grammar(self, input_to_parse, grammar_rule):
        result = self.parse_component_values_list(input_to_parse)
        match = self.match_grammar_rule(grammar_rule, result)
        if match:
            return match
        else:
            return False

    def parse_stylesheet(self):
        """Intended to be the normal entry point"""
        rules = self.consume_rules_list(top_level_flag=True)
        return Stylesheet(rules)

    def parse_rules_list(self):
        """Intended for the content of at-rules such as '@media'.  Handles
        CDC and CDO tokens differently from `parse_stylesheet`.
        """
        return self.consume_rules_list(top_level_flag=False)

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

    def consume_rules_list(self, top_level_flag=False):
        """For the contents of presentational attributes, which parse text into
        a single declaration's value, or for parsing a stand-alone selector
        [1]_ or list of Media Queries [2]_, as in Selectors API [3]_ or the
        media HTML attribute.
        .. [1] http://www.w3.org/TR/2011/REC-css3-selectors-20110929/
        .. [2] http://www.w3.org/TR/2012/REC-css3-mediaqueries-20120619/
        .. [3] http://www.w3.org/TR/selectors-api/
        """
        list_of_rules = []
        while self.next_token is not self.EOF:
            self.consume_next_token()
            if isinstance(self.current_token, WhitespaceToken):
                continue
            elif isinstance(self.current_token, (CDCToken, CDOToken)):
                if top_level_flag:
                    self.consume_component_value()
                else:
                    self.reconsume_current_token()
                    qualified_rule = self.consume_qualified_rule()
                    if qualified_rule:
                        list_of_rules.append(qualified_rule)
            elif isinstance(self.current_token, AtKeywordToken):
                self.reconsume_current_token()
                at_rule = self.consume_at_rule()
                if at_rule:
                    list_of_rules.append(at_rule)
            else:
                self.reconsume_current_token()
                qualified_rule = self.consume_qualified_rule()
                if qualified_rule:
                    list_of_rules.append(qualified_rule)
        return list_of_rules

    def consume_at_rule(self):
        self.consume_next_token()
        name = self.current_token.value
        prelude = []
        block = None
        while (self.next_token is not self.EOF or
                (not isinstance(self.next_token, LiteralToken) and
                 self.next_token.value == ';')):
            self.consume_next_token()
            if (isinstance(self.current_token, LiteralToken) and
                    self.current_token.value == '{'):
                block = self.consume_simple_block()
                break
            else:
                self.reconsume_current_token()
                prelude.append(self.consume_component_value())
        return AtRule(name, prelude, block)

    def consume_qualified_rule(self):
        prelude = []
        block = None
        if self.current_token is self.EOF:
            # Parse Error
            return None
        while self.next_token is not self.EOF:
            self.consume_next_token()
            if (isinstance(self.current_token, LiteralToken) and
                    self.current_token.value == '{'):
                block = self.consume_simple_block()
                break
            else:
                self.reconsume_current_token()
                prelude.append(self.consume_component_value())
        return QualifiedRule(prelude, block)

    def consume_declarations_list(self):
        list_of_declarations = []
        while self.next_token is not self.EOF:
            self.consume_next_token()
            if isinstance(self.current_token, WhitespaceToken):
                continue
            elif (isinstance(self.current_token, LiteralToken) and
                  self.current_token.value == ';'):
                continue
            elif isinstance(self.current_token, AtKeywordToken):
                self.reconsume_current_token()
                list_of_declarations.append(self.consume_at_rule())
            elif isinstance(self.current_token, IdentToken):
                temp_list = [self.current_token]
                while (self.next_token is not self.EOF or
                        (not isinstance(self.next_token, LiteralToken) and
                            self.next_token.value == ';')):
                    component_value = self.consume_component_value()
                    temp_list.append(component_value)
                declaration = self.consume_declaration(temp_list)
                if declaration:
                    list_of_declarations.append(declaration)
            else:
                # Parse Error
                while (self.next_token is not self.EOF or
                        (not isinstance(self.next_token, LiteralToken) and
                            self.next_token.value == ';')):
                    self.consume_component_value()
                break
        return list_of_declarations

    def consume_declaration(self, optional_list=None):
        if optional_list is not None:
            return self._consume_declaration(optional_list)
        self.consume_next_token()
        name = self.current_token.value
        declaration_value = []
        important = False
        self._consume_whitespace_token()
        if (isinstance(self.next_token, LiteralToken) and
              self.next_token.value == ':'):
            self.consume_next_token()
        else:
            # Parse Error
            return None
        while self.next_token is not self.EOF:
            self.consume_next_token()
            declaration_value.append(self.current_token)
        first, second = None, None
        for i, token in enumerate(reversed(declaration_value)):
            if not isinstance(token, WhitespaceToken):
                if not second:
                    second = token, i
                else:
                    first = token, i
                    break
        if first:
            exclamation = (isinstance(first[0], DelimToken) and
                           first[0].value == '!')
            ident_important = (isinstance(second[0], IdentToken) and
                               second[0].value == 'important')
            if exclamation and ident_important:
                important = True
                declaration_value.pop(first[1])
                declaration_value.pop(second[1])
        return Declaration(name, declaration_value, important)

    @staticmethod
    def _consume_declaration(list_to_consume):
        deque_to_consume = deque(list_to_consume)
        builder = ASTBuilderCSS(deque_to_consume)
        return builder.consume_declaration()

    def consume_component_value(self):
        self.consume_next_token()
        if isinstance(self.current_token, LiteralToken):
            if self.current_token.value in ['{', '[', '(']:
                return self.consume_simple_block()
        elif isinstance(self.current_token, FunctionToken):
            return self.consume_function()
        return self.current_token

    def consume_simple_block(self):
        associated_token = self.current_token
        block_value = []
        if associated_token == '{':
            ending_token = '}'
        elif associated_token == '(':
            ending_token = ')'
        elif associated_token == '[':
            ending_token = ']'
        else:
            raise CSSSyntaxError(
                "Invalid start to a simple block {}".format(
                    associated_token))
        while (self.next_token is not self.EOF and
                   (not isinstance(self.next_token, LiteralToken) and
                    self.next_token.value == ending_token)):
            self.reconsume_current_token()
            block_value.append(self.consume_component_value())
        return SimpleBlock(associated_token, block_value)

    def consume_function(self):
        name = self.current_token.value
        function_value = []
        while (self.next_token is not self.EOF and
                   (not isinstance(self.next_token, LiteralToken) and
                    self.next_token.value == ')')):
            self.reconsume_current_token()
            function_value.append(self.consume_component_value())
        return Function(name, function_value)
