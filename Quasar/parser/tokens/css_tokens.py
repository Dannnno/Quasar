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

from Quasar.parser.tokens import Token


logging.basicConfig(
    filename=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "css_token.log"),
    level=logging.INFO)

replace_characters = OrderedDict()
line_feed = u'u\000F'   # Line Feed
replacement_character = u'\uFFFD'   # Default replacement character
replace_characters[u'u\000Du\000F'] = line_feed   # Carriage Return + Line Feed
replace_characters[u'u\000D'] = line_feed   # Carriage Return (CR)
replace_characters[u'u\000C'] = line_feed   # Form Feed (FF)
replace_characters['\r\n'] = '\n'
replace_characters[u'u\0000'] = replacement_character

CSS_token_literals = {';': 'COLON',
                      ',': 'COMMA',
                      '[': 'LBRACK',
                      ']': 'RBRACK',
                      '(': 'LPAREN',
                      ')': 'RPAREN',
                      '{': 'LCURLY',
                      '}': 'RCURLY'}


def preprocessing(unicode_string, encoding='UTF_8'):
    unicode_string = unicode_string.decode(encoding)
    for replaced, replacer in replace_characters.iteritems():
        unicode_string = unicode_string.replace(replaced, replacer)
    return unicode_string


def numeric_token_chooser(char, stream):
    raise NotImplementedError


def ident_like_token_chooser(char, stream):
    raise NotImplementedError


def delim_token_chooser(char, stream):
    if char == '#':
        hash_type = 'unrestricted'
        first, second, third = stream.stream_peek(3)
        if ((first == '-' or
                CSSTokenizer.letters.match(first) or
                CSSTokenizer.numbers.match(first)) or
            (first == '\\' and
                not CSSTokenizer.newlines.match(second))):
            # Check if the next three are a valid identifier
            if first == '-':
                if (second == '-' or
                     (CSSTokenizer.letters.match(second) or
                         CSSTokenizer.numbers.match(second)) or
                     (second == '\\' and
                         not CSSTokenizer.newlines.match(third))):
                    hash_type = 'id'
            elif first == '\\':
                if (second == '-' or
                     (CSSTokenizer.letters.match(second) or
                         CSSTokenizer.numbers.match(second)) or
                     (second == '\\' and
                         not CSSTokenizer.newlines.match(third))):
                    hash_type = 'id'
            elif (CSSTokenizer.letters.match(first) or
                    CSSTokenizer.numbers.match(first)):
                if (second == '-' or
                     (CSSTokenizer.letters.match(second) or
                         CSSTokenizer.numbers.match(second)) or
                     (second == '\\' and
                         not CSSTokenizer.newlines.match(third))):
                    hash_type = 'id'
            result = ''
            next_char = stream.consume_raw_stream()
            while next_char:
                if (next_char == '-' or
                     (CSSTokenizer.letters.match(next_char) or
                         CSSTokenizer.numbers.match(next_char)) or
                     (next_char == '\\' and
                         not CSSTokenizer.newlines.match(next_char))):
                    result += next_char
                    try:
                        next_char = stream.consume_raw_stream()
                    except IndexError:
                        break
                else:
                    break
            return HashToken(result, type_=hash_type)
        else:
            return DelimToken(char)
    else:
        raise NotImplementedError


def string_chooser(char, stream):
    if char not in ['"', "'"]:
        raise ValueError("A string has to start with a quotation mark")
    quote_type = char
    string_token = ''
    next_char = stream.consume_raw_stream(1)
    while next_char != quote_type:
        if next_char in ['\n', '\r', '\f']:
            # An unescaped newline is a parse error
            if string_token[-1] != '\\':
                stream._stream.appendleft(next_char)
                return BadStringToken()
            string_token += '\\n'
        else:
            string_token += next_char
        next_char = stream.consume_raw_stream(1)
    return StringToken(string_token)


def url_chooser(char, stream):
    raise NotImplementedError


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

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)


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
        however is necessary for the inheritance tree and the way the function
        calls work.
        """
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


class HashToken(CSSToken):
    _type = "unrestricted"
    _value = ''
    _possible_types = ['id', 'unrestricted']

    def __init__(self, val, type_='unrestricted'):
        self.type_ = type_
        self.value = val

    @property
    def type_(self):
        return self._type

    @type_.setter
    def type_(self, type_):
        if type_ not in HashToken._possible_types:
            raise ValueError(
                "Type must be either 'id' or 'unrestricted', not {}".format(
                    type_))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    @property
    def match(self):
        return True


class StringToken(CSSToken):
    _regex = None
    _value = ''
    _match = None

    def __init__(self, string):
        self.value = string
        self._match = True

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, string):
        self._value = string

    @property
    def match(self):
        return self._match


class BadStringToken(StringToken):

    def __init__(self):
        super(BadStringToken, self).__init__('')


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


class DelimToken(CSSToken):
    _value = ''
    _match = None

    def __init__(self, char):
        self._value = char
        self._match = True

    @property
    def value(self):
        return self._value

    @property
    def match(self):
        return self._match


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
class PercentageToken(CSSToken):
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
            try:
                current = stream.consume_raw_stream()
            except IndexError:
                break
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
    instructions = {'(': LiteralToken, ')': LiteralToken, ',': LiteralToken,
                    ':': LiteralToken, ';': LiteralToken, '[': LiteralToken,
                    ']': LiteralToken, '{': LiteralToken, '}': LiteralToken,
                    ' ': WhitespaceToken,   # Whitespace is generalized as ' '
                    "'": string_chooser, '"': string_chooser,
                    '0': numeric_token_chooser,   # Numbers are generalized
                    'a': ident_like_token_chooser,  # 'Letters' are generalized
                    '#': delim_token_chooser,
                        # If the next input code point is a name code point or
                        # the next two input code points are a valid escape,
                        # then:
                        #      1. Create a <hash-token>.
                        #      2. If the next 3 input code points would start
                        #         an identifier, set the <hash-token>’s type
                        #         flag to "id".
                        #      3. Consume a name, and set the <hash-token>’s
                        #         value to the returned string.
                        #      4. Return the <hash-token>.
                    '$': delim_token_chooser,
                        # If the next token is U+003D EQUALS SIGN (=) then its
                        # a suffix match token
                    '*': delim_token_chooser,
                        # If the next token is U+003D EQUALS SIGN (=) then its
                        # a substring match token
                    '+': delim_token_chooser,
                        # If the stream started with a number, reconsume the
                        # current input code point, consume a numeric token and
                        # return it.
                    '-': delim_token_chooser,
                        # If the stream started with a number, reconsume the
                        # current input code point, consume a numeric token,
                        # and return it.  If the next 2 input code points are
                        # U+002D HYPHEN-MINUS U+003E GREATER-THAN SIGN (->),
                        # consume them and return a <CDC-token>.
                        # If the input stream starts with an identifier,
                        # reconsume the current input code point, consume an
                        # ident-like token, and return it.
                    '.': delim_token_chooser,
                        # If the input stream starts with a number, reconsume
                        # the current input code point, consume a numeric
                        # token, and return it.
                    '<': delim_token_chooser,
                        # If the next 3 input code points are U+0021
                        # EXCLAMATION MARK U+002D HYPHEN-MINUS U+002D
                        # HYPHEN-MINUS (!--), consume them and return a
                        # <CDO-token>.
                    '@': delim_token_chooser,
                        # If the next 3 input code points would start an
                        # identifier, consume a name, create an
                        # <at-keyword-token> with its value set to the returned
                        #  value, and return it.
                    '\\': delim_token_chooser,
                        # If the input stream starts with a valid escape,
                        # reconsume the current input code point, consume an
                        # ident-like token, and return it.  Otherwise, this is
                        # a parse error. Return a <delim-token> with its value
                        # set to the current input code point.
                    '^': delim_token_chooser,
                        # If the next input code point is U+003D EQUALS SIGN
                        # (=), consume it and return a <prefix-match-token>.
                    '|': delim_token_chooser,
                        # If the next input code point is U+003D EQUALS SIGN
                        # (=), consume it and return a <dash-match-token>.
                        # Otherwise, if the next input code point is U+0073
                        # VERTICAL LINE (|), consume it and return a
                        # <column-token>.
                    '~': delim_token_chooser
                        # If the next input code point is U+003D EQUALS SIGN
                        # (=), consume it and return an <include-match-token>.
                    }
    whitespace = re.compile('\s')
    letters = re.compile('[a-zA-Z_]')
    numbers = re.compile('\d')
    newlines = re.compile('[\n\r\f]')
    EOF = re.compile('\Z')

    _stream = None
    _current = None

    def __init__(self, iterable=()):
        if isinstance(iterable, basestring):
            iterable = preprocessing(iterable)
        else:
            iterable = ''.join(map(preprocessing, iterable))
        self.tokens = deque()
        self.stream = deque(iterable)

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        if self.stream is None:
            self._stream = deque(value)
        else:
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
                elif self._current in CSSTokenizer.instructions:
                    token_type = CSSTokenizer.instructions[self._current]
                elif CSSTokenizer.EOF.match(self._current):
                    token_type = EOFToken()
                else:
                    token_type = delim_token_chooser
            except KeyError as e:
                logging.warn(
                    "Unknown character `{}`.  Skipping".format(self._current))
            else:
                self.tokens.append(token_type(self._current, self))

    def consume_token(self):
        return self.tokens.popleft()

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
                return consumed
            number -= 1
        return consumed

