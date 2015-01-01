from Quasar.parser.ast import ASTNode
from Quasar.parser.tokens.css_tokens import CSSTokenizer


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

    def parse_token_stream(self):
        while self.css_token_stream:
            pass

    def parse_stylesheet(self):
        pass

    def parse_rules_list(self):
        pass

    def parse_rule(self):
        pass

    def parse_declarations_list(self):
        pass

    def parse_declaration(self):
        pass

    def parse_component_values_list(self):
        pass

    def parse_component_value(self):
        pass

    def consume_rules_list(self):
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