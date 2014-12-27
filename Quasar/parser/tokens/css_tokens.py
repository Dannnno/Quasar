# -*- coding: utf-8 -*-
# Implemented as per http://dev.w3.org/csswg/css-syntax/#tokenizing-and-parsing

"""
4. Tokenization

Implementations must act as if they used the following algorithms to tokenize
CSS. To transform a stream of code points into a stream of tokens, repeatedly
consume a token until an <EOF-token> is reached, collecting the returned tokens
into a stream. Each call to the consume a token algorithm returns a single
token, so it can also be used "on-demand" to tokenize a stream of code points
during parsing, if so desired.

The output of the tokenization step is a stream of zero or more of the
following tokens:

    <ident-token>, <function-token>, <at-keyword-token>, <hash-token>,
    <string-token>, <bad-string-token>, <url-token>, <bad-url-token>,
    <delim-token>, <number-token>, <percentage-token>, <dimension-token>,
    <include-match-token>, <dash-match-token>, <prefix-match-token>,
    <suffix-match-token>, <substring-match-token>, <column-token>,
    <whitespace-token>, <CDO-token>, <CDC-token>, <colon-token>,
    <semicolon-token>, <comma-token>, <[-token>, <]-token>, <(-token>,
    <)-token>, <{-token>, and <}-token>.

Details on those tokens:

    <ident-token>, <function-token>, <at-keyword-token>, <hash-token>,
      <string-token>, <url-token>:
        - Have a value composed of zero or more code points.
        - <hash-token>s have a type flag set to either "id" or "unrestricted".
          The type flag defaults to "unrestricted"

    <delim-token> has a value composed of a single code point.

    <number-token>, <percentage-token>, <dimension-token>:
        - Have a representation composed of one or more code points, and a
          numeric value.
        - <number-token> and <dimension-token> additionally have a type flag
          set to either "integer" or "number".
            - The type flag defaults to "integer" if not otherwise set.
        - <dimension-token> additionally have a unit composed of one or more
          code points.
"""
from collections import OrderedDict, deque
import logging
import re

from Quasar import parse_log_file


logging.basicConfig(filename=parse_log_file, level=logging.INFO)

replace_characters = OrderedDict()
line_feed = u'\u000A'   # New line (\n)
replacement_character = u'\uFFFD'   # Default replacement character (�)
replace_characters[u'\u000D\u000A'] = line_feed   # Carriage Return + New Line
replace_characters[u'\u000D\u000F'] = line_feed   # Carriage Return + Line Feed
replace_characters[u'\u000D'] = line_feed   # Carriage Return (CR)
replace_characters[u'\u000C'] = line_feed   # Form Feed (FF)
replace_characters[u'\u0000'] = replacement_character


def preprocessing(unicode_string):
    try:
        unicode_string = unicode_string.decode('UTF-8')
    except UnicodeDecodeError:
        logging.warn("CSS contains invalid characters for UTF-8")
        acc_unicode_string = ''
        for code_point in unicode_string:
            try:
                acc_unicode_string += code_point.decode('UTF-8')
            except UnicodeDecodeError:
                # Skip invalid characters
                pass
        unicode_string = acc_unicode_string
    for replaced, replacer in replace_characters.iteritems():
        unicode_string = unicode_string.replace(replaced, replacer)
    return unicode_string


class CSSToken(object):

    def __init__(self, string):
        self.value = string

    def __str__(self):
        return self.value

    def __repr__(self):
        return repr(str(self))


class WhitespaceToken(CSSToken):

    def __init__(self):
        super(WhitespaceToken, self).__init__(' ')


class NumberToken(CSSToken):

    def __init__(self, string_repr, numeric_value, type_flag):
        self.string = string_repr
        self.value = numeric_value
        self.type_ = type_flag

    def __str__(self):
        return self.string


class DimensionToken(NumberToken):

    def __init__(self, string_repr, numeric_value, type_flag, unit):
        super(DimensionToken, self).__init__(
            string_repr, numeric_value, type_flag)
        self.unit = unit

    def __str__(self):
        return "{} {}".format(super(DimensionToken, self).__str__(), self.unit)


class PercentageToken(NumberToken):

    def __init__(self, string_repr, numeric_value):
        super(PercentageToken, self).__init__(string_repr, numeric_value, None)

    def __str__(self):
        return "{} %".format(super(PercentageToken, self).__str__())


class CSSTokenizer(object):
    digit = re.compile(u'[\u0030-\u0039]')
    hex_digit = re.compile(u'[\u0030-\u0039\u0041-\u0046\u0061-\u0066]')
    uppercase_letter = re.compile(u'[\u0041-\u005A]')
    lowercase_letter = re.compile(u'[\u0061-\u007A]')
    letter = re.compile(u'[\u0041-\u0051\u0061-\u007A]')
    non_ascii = re.compile(u'[^\u0000-\u007F]')
    name_start = re.compile(u'''[\u0041-\u0051\u0061-\u007A\u005F]|
                                [^\u0000-\u007F]
                             ''', re.VERBOSE)
    name = re.compile(u'''[\u0041-\u0051\u0061-\u007A\u005F]|
                          [^\u0000-\u007F]|[\u0030-\u0039]|\u002D
                       ''', re.VERBOSE)
    non_printable = re.compile(u'[\u0000-\u0008\u000B\u000E-\u001F\u007F]')
    newline = re.compile(u'\u000A')
    whitespace = re.compile(u'[\u000A\u0009\u0020]')
    surrogate = re.compile(u'[\uD800-\uDFFF]')
    literal_tokens = re.compile(u'''\u0028|\u0029|\u002C|\u003A|\u003B|\u005B|
                                    \u005D|\u007B|\u007D
                                 ''', re.VERBOSE)
    quotations = re.compile(u'[\u0022\u0027]')
    hash_token = u'\u0023'   # A `#` character
    forward_slash = u'\u002F'
    dollar_sign = u'\u0024'
    asterisk = u'\u002A'
    plus = u'\u002B'
    minus = u'\u002D'
    full_stop = u'\u002E'
    less_than = u'\u003C'
    at_sign = u'\u0040'
    backslash = u'\u005C'
    circumflex = u'\u005E'
    vertical = u'\u007C'
    tilde = u'\u007E'
    percent = u'\u0025'
    EOF = None

    _stream = None
    _tokens = None
    _current = None
    _next = ''

    def __init__(self, input_string):
        self.tokens = deque()
        self.stream = input_string
        self.current_code_point = ''
        self.next_code_point = self.stream

    @property
    def stream(self):
        return self._stream

    @stream.setter
    def stream(self, value):
        self._stream = deque(preprocessing(value))

    @property
    def tokens(self):
        return self._tokens

    @tokens.setter
    def tokens(self, iterable):
        if self._tokens is None:
            self._tokens = deque()
        self._tokens.extend(iterable)

    @property
    def current_code_point(self):
        return self._current

    @current_code_point.setter
    def current_code_point(self, new_code_point):
        self._current = new_code_point

    @property
    def next_code_point(self):
        return self._next

    @next_code_point.setter
    def next_code_point(self, stream):
        try:
            self._next = stream[0]
        except IndexError:
            self._next = CSSTokenizer.EOF

    def tokenize_stream(self):
        while self.stream:
            if self.next_code_point is None:
                break
            self.consume_next_code_point()
            if self.current_code_point == CSSTokenizer.forward_slash:
                self.consume_comment()
            elif CSSTokenizer.whitespace.match(self.current_code_point):
                self.consume_whitespace_token()
            elif (CSSTokenizer.digit.match(self.current_code_point) or
                    self.current_code_point == CSSTokenizer.plus or
                    self.current_code_point == CSSTokenizer.minus or
                    self.current_code_point == CSSTokenizer.full_stop):
                self.consume_numeric_token()
            elif CSSTokenizer.name_start.match(self.current_code_point):
                self.consume_ident_like_token()
            elif CSSTokenizer.literal_tokens.match(self.current_code_point):
                self.consume_literal_token()
            elif CSSTokenizer.quotations.match(self.current_code_point):
                self.consume_string_token()
            elif self.current_code_point == CSSTokenizer.hash_token:
                self.consume_hash_token()
            elif self.current_code_point == CSSTokenizer.dollar_sign:
                self.consume_suffix_match_token()
            elif self.current_code_point == CSSTokenizer.asterisk:
                self.consume_substring_match_token()
            elif self.current_code_point == CSSTokenizer.less_than:
                self.consume_CDO_token()
            elif self.current_code_point == CSSTokenizer.backslash:
                self.consume_escape_token()
            elif self.current_code_point == CSSTokenizer.circumflex:
                self.consume_prefix_match_token()
            elif self.current_code_point == CSSTokenizer.vertical:
                self.consume_dash_match_token()
            elif self.current_code_point == CSSTokenizer.tilde:
                self.consume_include_match_token()
            else:
                self.consume_delim_token()

    def lookahead(self, distance):
        peek = []
        for i in range(distance):
            try:
                peek.append(self.stream[i])
            except IndexError:
                peek.append(None)
        return peek

    def consume_next_code_point(self):
        self.current_code_point = self.stream.popleft()
        self.next_code_point = self.stream

    def reconsume_current_code_point(self):
        self.stream.appendleft(self.current_code_point)
        self.current_code_point = None
        self.next_code_point = self.stream

    def _starts_identifier(self):
        first, second, third = [self.current_code_point] + self.lookahead(2)
        if first == CSSTokenizer.minus:
            if CSSTokenizer.name_start.match(second):
                return True
            elif second == CSSTokenizer.minus:
                return True
            elif self._valid_escape(second, third):
                return True
        elif CSSTokenizer.name_start.match(first):
            return True
        elif self._valid_escape(first, second):
            return True
        return False

    @staticmethod
    def _valid_escape(first, second):
        if first == CSSTokenizer.backslash:
            if not CSSTokenizer.newline.match(second):
                return True
        return False

    def consume_comment(self):
        ending_asterisk = False
        if self.next_code_point == CSSTokenizer.asterisk:
            while self.next_code_point is not None:
                self.consume_next_code_point()
                if ending_asterisk:
                    if self.current_code_point == CSSTokenizer.forward_slash:
                        return
                    else:
                        ending_asterisk = False
                if self.current_code_point == CSSTokenizer.asterisk:
                    ending_asterisk = True
        else:
            self.consume_delim_token()

    def consume_whitespace_token(self):
        self.tokens.append(WhitespaceToken())
        while (self.next_code_point is not None and
                CSSTokenizer.whitespace.match(self.next_code_point)):
            self.consume_next_code_point()

    def _consume_digits(self):
        digit_string = ''
        if CSSTokenizer.digit.match(self.current_code_point):
            digit_string += self.current_code_point
        while CSSTokenizer.digit.match(self.next_code_point):
            self.consume_next_code_point()
            digit_string += self.current_code_point
            if self.next_code_point is None:
                break
        return digit_string

    def _consume_number(self):
        string_representation = ''
        type_flag = 'integer'

        # Optional sign of the number
        if self.current_code_point in [CSSTokenizer.plus, CSSTokenizer.minus]:
            string_representation += self.current_code_point

        # Value before the decimal point
        string_representation += self._consume_digits()

        # Values after the decimal point
        if CSSTokenizer.full_stop == self.next_code_point:
            self.consume_next_code_point()
            if CSSTokenizer.digit.match(self.next_code_point):
                type_flag = 'number'
                string_representation += self.current_code_point
                string_representation += self._consume_digits()

        # Scientific notation
        if self.next_code_point in ['e', 'E']:
            possible_scientific_notation = ''
            self.consume_next_code_point()
            possible_scientific_notation += self.current_code_point

            # Optional sign of the number
            if self.next_code_point in [CSSTokenizer.plus, CSSTokenizer.minus]:
                self.consume_next_code_point()
                possible_scientific_notation += self.current_code_point

            # Values after the (optional) sign
            if CSSTokenizer.digit.match(self.next_code_point):
                type_flag = 'number'
                possible_scientific_notation += self._consume_digits()
                string_representation += possible_scientific_notation

        if type_flag == 'number':
            numeric_value = float(string_representation)
        else:
            numeric_value = int(string_representation)

        return string_representation, numeric_value, type_flag

    def consume_numeric_token(self):
        string_repr, numeric_value, type_flag = self._consume_number()
        if self.next_code_point == CSSTokenizer.percent:
            self.consume_next_code_point()
            self.tokens.append(PercentageToken(string_repr, numeric_value))
        else:
            if self.next_code_point is not None:
                self.consume_next_code_point()
                if self._starts_identifier():
                    name = self.current_code_point + self._consume_name()
                    self.tokens.append(DimensionToken(
                        string_repr, numeric_value, type_flag, name))
            else:
                self.tokens.append(
                    NumberToken(string_repr, numeric_value, type_flag))

    def _consume_name(self):
        result = ''
        while self.stream:
            self.consume_next_code_point()
            if CSSTokenizer.name.match(self.current_code_point):
                result += self.current_code_point
            elif self._valid_escape(self.current_code_point,
                                    self.next_code_point):
                result += self.consume_escape_token()
            else:
                self.reconsume_current_code_point()
                break
        return result

    def consume_ident_like_token(self):
        pass

    def consume_literal_token(self):
        pass

    def consume_string_token(self):
        pass

    def consume_hash_token(self):
        pass

    def consume_prefix_match_token(self):
        pass

    def consume_suffix_match_token(self):
        pass

    def consume_substring_match_token(self):
        pass

    def consume_CDO_token(self):
        pass

    def consume_escape_token(self):
        self.consume_next_code_point()
        return self.current_code_point

    def consume_dash_match_token(self):
        pass

    def consume_include_match_token(self):
        pass

    def consume_delim_token(self):
        pass
