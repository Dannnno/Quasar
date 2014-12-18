# -*- coding: utf-8 -*-
# Implemented as per http://dev.w3.org/csswg/css-syntax/#tokenizing-and-parsing

"""
4. Tokenization

Implementations must act as if they used the following algorithms to tokenize CSS. To transform a stream of code points
into a stream of tokens, repeatedly consume a token until an <EOF-token> is reached, collecting the returned tokens into
 a stream. Each call to the consume a token algorithm returns a single token, so it can also be used "on-demand" to
 tokenize a stream of code points during parsing, if so desired.

The output of the tokenization step is a stream of zero or more of the following tokens:

    <ident-token>, <function-token>, <at-keyword-token>, <hash-token>, <string-token>, <bad-string-token>,
    <url-token>, <bad-url-token>, <delim-token>, <number-token>, <percentage-token>, <dimension-token>,
    <include-match-token>, <dash-match-token>, <prefix-match-token>, <suffix-match-token>, <substring-match-token>,
    <column-token>, <whitespace-token>, <CDO-token>, <CDC-token>, <colon-token>, <semicolon-token>, <comma-token>,
    <[-token>, <]-token>, <(-token>, <)-token>, <{-token>, and <}-token>.

Details on those tokens:

    <ident-token>, <function-token>, <at-keyword-token>, <hash-token>, <string-token>, <url-token>:
        - Have a value composed of zero or more code points.
        - <hash-token>s have a type flag set to either "id" or "unrestricted". The type flag defaults to "unrestricted"

    <delim-token> has a value composed of a single code point.

    <number-token>, <percentage-token>, <dimension-token>:
        - Have a representation composed of one or more code points, and a numeric value.
        - <number-token> and <dimension-token> additionally have a type flag set to either "integer" or "number".
            - The type flag defaults to "integer" if not otherwise set.
        - <dimension-token> additionally have a unit composed of one or more code points.
"""
from collections import OrderedDict, deque
import abc
import logging
import os
import re

from WebBrowser.parser.tokens.tokens import Token


logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "css_token.log"),
                    level=logging.INFO)


replace_characters = OrderedDict()
line_feed = u'u\000F' # Line Feed
replacement_character = u'\uFFFD'
replace_characters[u'u\000Du\000F'] = line_feed   # Carriage Return + Line Feed
replace_characters[u'u\000D'] = line_feed   # Carriage Return (CR)
replace_characters[u'u\000C'] = line_feed   # Form Feed (FF)
replace_characters[u'u\0000'] = replacement_character

CSS_token_literals = {';': 'COLON',
                      ',': 'COMMA',
                      '[': 'LBRACK',
                      ']': 'RBRACK',
                      '(': 'LPAREN',
                      ')': 'RPAREN',
                      '{': 'LCURLY',
                      '}': 'RCURLY'}

CSS_tokens = {"<ident-token>": re.compile("""
                                      (?:--|-|\A) # an ident can start with an optional -/--
                                      ([^\x00-\x7F]   # This matches non ascii characters
                                       |
                                       [a-zA-Z_]|-   # Otherwise we match letters mostly
                                       |
                                       (\\\\[^a-fA-F0-9\r\n\f]\Z|\\\\[a-fA-F0-9](?:\Z|\s))   # Escape token below
                                      )+
                                          """, re.VERBOSE),
              "<function-token>":
                 # This is just the ident-token plus an open paren
                 re.compile("-{,2}([^\x00-\x7F]|[a-zA-Z_\\\\-]|(\\[^a-fA-F0-9\r\n\f]\Z|\\[a-fA-F0-9](?:\Z|\s)))+\("),
              "<at-keyword-token>":
                 # This is just an @ sign plus the ident-token
                 re.compile("@-{,2}([^\x00-\x7F]|[a-zA-Z_\\\\-]|(\\[^a-fA-F0-9\r\n\f]\Z|\\[a-fA-F0-9](?:\Z|\s)))+"),
              "<hash-token>": # This is just a # sign plus a word or escape sequence
                              re.compile("""
                                     [#]   # Matching the hash sign
                                     ([^\x00-\x7F]   # This matches non ascii characters
                                      |
                                      [a-zA-Z0-9]|-   # Otherwise we match a word-character
                                      |
                                      (\\\\([^a-fA-F0-9\r\n\f]\Z)|([a-fA-F0-9](?:\Z|\s))))+   # Escape token below
                                         """, re.VERBOSE),
              "<string-token>": re.compile("""
                                      (?P<quote> "|')   # which we start with
                                      ([^(?P=<quote>)\\\n\r\f]   # strings, but not multiline
                                       |
                                       \\\\([^a-fA-F0-9\r\n\f]\Z)|([a-fA-F0-9](?:\Z|\s))   # Escape token below
                                       |
                                       \\\\[\n\r\f]|\\\\\r\n   # Collecting escaped newlines
                                      )+
                                      [(?P=<quote>)]\Z  # which we started with
                                           """, re.VERBOSE),
              "<bad-string-token>": None,
              "<url-token>": re.compile("""
                                       url   # starts with url
                                       \(   # lparen
                                        \s*   # optional whitespace
                                        ([^"'\\\\\s]   #not quotes, slashes or newlines
                                         |
                                         (\\\\([^a-fA-F0-9\r\n\f]\Z)|([a-fA-F0-9](?:\Z|\s))))*  # Escape token below
                                        \s*   # optional whitespace
                                       \)   # endparen
                                        """, re.VERBOSE),
              "<comment-token>": re.compile(r"""
                                        /   # match the leading slash
                                        \*   # match the opening star
                                        ([^*])*   # match anything but a star, optionally
                                        \*   # match the ending star
                                        /   # match the ending slash
                                             """, re.VERBOSE),
              "<hex-digit-token>": re.compile("[a-fA-F0-9]\Z"),
              "<escape-token>": re.compile("""
                                       \\\\   # always starts with a backslash
                                       ([^a-fA-F0-9\r\n\f]\Z   # escaping symbols and spaces
                                        |
                                        [a-fA-F0-9](?:\Z|\s+))   # 1-6 hex digits followed by optional whitespace
                                           """, re.VERBOSE),
              "<newline-token>": re.compile("""
                                            [\n\r\f]{1}(\n|\Z)
                                            """, re.VERBOSE)
}


def preprocessing(unicode_string, encoding='UTF_8'):
    unicode_string = unicode_string.decode(encoding)
    for replaced, replacer in replace_characters.iteritems():
        unicode_string = unicode_string.replace(replaced, replacer)
    return unicode_string


class CSSToken(object):
    __metaclass__ = Token
    _value = ''
    _match = None
    _stream = deque()

    def __init__(self, first, token_stream):
        self.first = first
        self.stream = token_stream

    @property
    def regex(self):
        return self._regex

    @property
    def value(self):
        return self._value

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, stream_):
        if isinstance(stream_, CSSTokenizer):
            self._stream = stream_
        else:
            self._stream = CSSTokenizer(stream_)

    @abc.abstractproperty
    def match(self):
        return self._match

    def tokenize(self):
        self.match = self.stream
        self.value = self.match


# Todo: implement
class LiteralToken(CSSToken):
    _regex = re.compile(r'[;:,\[\]\(\)\{\}]')
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(LiteralToken, self).__init__(first, stream)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, regex_match):
        if regex_match:
            self._value = ' '
        else:
            self._value = None

    @property
    def match(self):
        return self._match

    @match.setter
    def match(self, stream):
        current = stream.popleft()
        consumed = []
        while self.regex.match(current):
            pass


# Todo: implement
class IdentToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(IdentToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class FunctionToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(FunctionToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class AtKeywordToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(AtKeywordToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class HashToken(CSSToken):
    _type = "unrestricted"
    _possible_types = ['id', 'unrestricted']

    def __init__(self, first='', stream=deque()):
        super(HashToken, self).__init__(first, stream)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type_):
        if type_ not in HashToken._possible_types:
            raise ValueError("Type must be either 'id' or 'unrestricted', not {}".format(type_))


# Todo: implement
class StringToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(StringToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class URLToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(URLToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class DelimToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(DelimToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class NumberToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(NumberToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class PercentageToken(NumberToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(PercentageToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class DimensionToken(NumberToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(DimensionToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class IncludeMatchToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(IncludeMatchToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class DashMatchToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(DashMatchToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class PrefixMatchToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(PrefixMatchToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class SuffixMatchToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(SuffixMatchToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class SubstringMatchToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(SubstringMatchToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class ColumnToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(ColumnToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


class WhitespaceToken(CSSToken):
    _regex = re.compile(r'(\s+)')
    _value = ' '
    _match = None

    def __init__(self, first='', stream=deque()):
        super(WhitespaceToken, self).__init__(first, stream)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, regex_match):
        if regex_match:
            self._value = ' '
        else:
            self._value = None

    @property
    def match(self):
        return self._match

    @match.setter
    def match(self, stream):
        matched = ""
        current = self.first
        while self.regex.match(current):
            matched += current
            current = stream.consume_token()
        if matched:
            self._match = True


# Todo: implement
class CDOToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(CDOToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class CDCToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(CDCToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class CommentToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(CommentToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class HexDigitToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(HexDigitToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class EscapeToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(EscapeToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


# Todo: implement
class NewlineToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(NewlineToken, self).__init__(first, stream)

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, regex_match):
        raise NotImplementedError

    @property
    def match(self):
        raise NotImplementedError

    @match.setter
    def match(self, stream):
        raise NotImplementedError


class CSSTokenizer(object):
    _stream = deque()
    instructions = {' ': WhitespaceToken, "'": StringToken, '"': StringToken,
                    u'\u0022': StringToken, u'\u0023': StringToken}

    def __init__(self, iterable=()):
        self.tokens = deque()
        self.stream = iterable
        self.tokenize_stream()

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        self._stream.extend(value)

    def tokenize_stream(self):
        while self.stream:
            current = self.consume_raw_stream(1)
            try:
                if current in CSS_token_literals:
                    self.tokens.append(LiteralToken(CSS_token_literals[current]))
                    continue
                if WhitespaceToken._regex.match(current):
                    current = ' '
                token_type = CSSTokenizer.instructions[current]
            except KeyError as e:
                logging.warn("Unknown character `{}`.  Skipping".format(current))
            else:
                self.tokens.append(token_type(current, self.stream))

    def consume_token(self, number=1):
        return CSSTokenizer._consume(self.tokens, number)

    def consume_raw_stream(self, number=1):
        return CSSTokenizer._consume(self.stream, number)

    def token_peek(self, number=1):
        return CSSTokenizer._lookahead(self.tokens, number)

    def stream_peek(self, number=1):
        return CSSTokenizer._lookahead(self.stream, number)

    @staticmethod
    def _lookahead(deq, number):
        consumed = [deq.popleft() for _ in xrange(number)]
        deq.extendleft(consumed[::-1])
        return consumed

    @staticmethod
    def _consume(deq, number):
        consumed = ''
        while number > 0:
            try:
                consumed += deq.popleft()
            except IndexError:
                # Deque is empty
                return consumed
            number -= 1
        return consumed

