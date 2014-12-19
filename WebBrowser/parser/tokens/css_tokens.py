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
line_feed = u'u\000F'   # Line Feed
replacement_character = u'\uFFFD'   # Default replacement character
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

## Token meta classes
# class DelimTokenMeta(Token):
#
#     def __init__(self, clsname, base, dct, current_char, stream):
#         pass
#
#     def __new__(cls, clsname, base, dct, current_char, stream):
#         return super(DelimTokenMeta, cls).__new__(cls, clsname, base, dct)
#
#
# class IdentLikeToken(Token):
#
#     def __init__(self, clsname, base, dct, current_char, stream):
#         pass
#
#     def __new__(cls, clsname, base, dct, current_char, stream):
#         return super(IdentLikeToken, cls).__new__(cls, clsname, base, dct)
#
#
# class NumericToken(Token):
#
#     def __init__(self, clsname, base, dct, current_char, stream):
#         pass
#
#     def __new__(cls, clsname, base, dct, current_char, stream):
#         return super(NumericToken, cls).__new__(cls, clsname, base, dct)
#
#
# class StringToken(Token):
#
#     def __init__(self, clsname, base, dct, current_char, stream):
#         pass
#
#     def __new__(cls, clsname, base, dct, current_char, stream):
#         print cls, clsname, base, dct, current_char, stream
#         return super(StringToken, cls).__new__(cls, clsname, base, dct)
#
#
# class URLToken(Token):
#     # __metaclass__ = IdentLikeToken
#
#     def __init__(self, clsname, base, dct, current_char, stream):
#         pass
#
#     def __new__(cls, clsname, base, dct, current_char, stream):
#         return super(URLToken, cls).__new__(cls, clsname, base, dct)


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


class LiteralToken(CSSToken):
    _regex = re.compile('[,:;\(\)\[\{\]\}]')
    _value = None
    _match = None

    def __init__(self, first, stream=deque()):
        if self.regex.match(first):
            self._value = first
            self._match = True
        else:
            raise ValueError("Not a literal, is a {}".format(first))

    @property
    def value(self):
        return self._value

    @property
    def match(self):
        return self._match

    def tokenize(self):
        """This function is unnecessary because literals can get skipped,
        however is necessary for the inheritance tree and the way the function calls work
        """
        pass


# Todo: implement
class IdentToken(CSSToken):
    #_metaclass__ = IdentLikeToken
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
    #_metaclass__ = IdentLikeToken
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
class GoodStringToken(CSSToken):
    #_metaclass__ = StringToken
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(GoodStringToken, self).__init__(first, stream)

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
class BadStringToken(CSSToken):
    #_metaclass__ = StringToken
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(BadStringToken, self).__init__(first, stream)

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
class GoodURLToken(CSSToken):
    #_metaclass__ = URLToken
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(GoodURLToken, self).__init__(first, stream)

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
class BadURLToken(CSSToken):
    #_metaclass__ = URLToken
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(BadURLToken, self).__init__(first, stream)

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
    #_metaclass__ = DelimTokenMeta
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
    #_metaclass__ = NumericToken
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
class PercentageToken(CSSToken):
    #_metaclass__ = NumericToken
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
class DimensionToken(CSSToken):
    #_metaclass__ = NumericToken
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


# Todo: implement
class EOFToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, first='', stream=deque()):
        super(EOFToken, self).__init__(first, stream)

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
    whitespace = re.compile('\s')
    letters = re.compile('[a-zA-Z_]')
    numbers = re.compile('\d')
    EOF = re.compile('\Z')
    _stream = deque()
    _current = None
    # In all cases a DelimToken has more than one possible option.  I'm not positive how I'm going to handle this.  I
    # can sort of imagine some metaclass wizardry, or make DelimToken a function instead of a class and then have it
    # return a DToken object (or something) if all else fails.  That sort of sounds like metaclass wizardry though
    instructions = {'(': LiteralToken, ')': LiteralToken, ',': LiteralToken, ':': LiteralToken, ';': LiteralToken,
                    '[': LiteralToken, ']': LiteralToken, '{': LiteralToken, '}': LiteralToken,
                    ' ': WhitespaceToken,   # All whitespace is generalized into a single space (in tokenize_stream)
                    # "'": StringToken("GoodStringToken", (CSSToken,), {}, _current, _stream),
                    # '"': StringToken("GoodStringToken", (CSSToken,), {}, _current, _stream),
                    # '0': NumericToken,   # This is handled below, all numbers are this entry
                    # 'a': IdentLikeToken,   # This is handled below, all letters and the `_` are this entry
                    # '#': DelimTokenMeta,   # If the next input code point is a name code point or the next two input code
                    #                    # points are a valid escape, then:
                    #                    #      1. Create a <hash-token>.
                    #                    #      2. If the next 3 input code points would start an identifier, set the
                    #                    #      <hash-token>’s type flag to "id".
                    #                    #      3. Consume a name, and set the <hash-token>’s value to the returned string.
                    #                    #      4. Return the <hash-token>.
                    # '$': DelimTokenMeta,   # If the next token is U+003D EQUALS SIGN (=) then its a suffix match token
                    # '*': DelimTokenMeta,   # If the next token is U+003D EQUALS SIGN (=) then its a substring match token
                    # '+': DelimTokenMeta,   # If the stream started with a number, reconsume the current input code point,
                    #                    # consume a numeric token and return it.
                    # '-': DelimTokenMeta,   # If the stream started with a number, reconsume the current input code point,
                    #                    # consume a numeric token, and return it.
                    #                    # If the next 2 input code points are:
                    #                    #  U+002D HYPHEN-MINUS U+003E GREATER-THAN SIGN (->),
                    #                    # consume them and return a <CDC-token>.
                    #                    # If the input stream starts with an identifier, reconsume the current input
                    #                    # code point, consume an ident-like token, and return it.
                    # '.': DelimTokenMeta,   # If the input stream starts with a number, reconsume the current input code
                    #                    # point, consume a numeric token, and return it.
                    # '<': DelimTokenMeta,   # If the next 3 input code points are U+0021 EXCLAMATION MARK U+002D HYPHEN-MINUS
                    #                    # U+002D HYPHEN-MINUS (!--), consume them and return a <CDO-token>.
                    # '@': DelimTokenMeta,   # If the next 3 input code points would start an identifier, consume a name,
                    #                    # create an <at-keyword-token> with its value set to the returned value,
                    #                    # and return it.
                    # '\\': DelimTokenMeta,  # If the input stream starts with a valid escape, reconsume the current input
                    #                    # code point, consume an ident-like token, and return it.  Otherwise, this is a
                    #                    # parse error. Return a <delim-token> with its value set to the current input
                    #                    # code point.
                    # '^': DelimTokenMeta,   # If the next input code point is U+003D EQUALS SIGN (=), consume it and return
                    #                    # a <prefix-match-token>.
                    # '|': DelimTokenMeta,   # If the next input code point is U+003D EQUALS SIGN (=), consume it and return a
                    #                    # <dash-match-token>.
                    #                    # Otherwise, if the next input code point is U+0073 VERTICAL LINE (|), consume it
                    #                    # and return a <column-token>.
                    # '~': DelimTokenMeta   # If the next input code point is U+003D EQUALS SIGN (=), consume it and return
                    #                    # an <include-match-token>.
                    }

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
            self._current = self.consume_raw_stream(1)
            try:
                if CSSTokenizer.whitespace.match(self._current):
                    token_type = CSSTokenizer.instructions[' ']
                elif CSSTokenizer.numbers.match(self._current):
                    token_type = CSSTokenizer.instructions['0']
                elif CSSTokenizer.letters.match(self._current):
                    token_type = CSSTokenizer.instructions['a']
                elif CSSTokenizer.EOF.match(self._current):
                    token_type = EOFToken()
                else:
                    token_type = DelimToken(self._current)
            except KeyError as e:
                logging.warn("Unknown character `{}`.  Skipping".format(self._current))
            else:
                self.tokens.append(token_type(self._current, self.stream))

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

