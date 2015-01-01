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
line_feed = u'\u000A'   # (\n)
replacement_character = u'\uFFFD'   # Default replacement character (�)
replace_characters[u'\u000D\u000A'] = line_feed   # Carriage Return + New Line
replace_characters[u'\u000D'] = line_feed   # Carriage Return (CR)
replace_characters[u'\u000C'] = line_feed   # Form Feed (FF)
replace_characters[u'\u0000'] = replacement_character


def preprocessing(unicode_string_input):
    """Preprocesses the CSS to handle invalid or undesirable code points.

    Parameters
    ----------
    unicode_string_input : unicode
        A string that holds a CSS document or CSS information, encoded using
        UTF-8.

    Returns
    -------
    unicode_string_output : unicode
        The processed CSS

    Notes
    -----
    - Invalid code points are defined by the current UTF-8 standard; any value
      greater than U+10FFFF is invalid and is skipped by the algorithm.
    - Undesirable code points and their replacements are:
         | U+000D U+000A Carriage Return + Line Feed -> U+000A Line Feed
         | U+000D Carriage Return -> U+000A Line Feed
         | U+000C Form Feed -> U+000A Line Feed
         | U+0000 Null -> U+FFFD Replacement Character (�)
    """

    try:
        unicode_string_output = unicode_string_input.decode('UTF-8')
    except UnicodeDecodeError:
        logging.warn("CSS contains invalid characters for UTF-8")
        acc_unicode_string = ''
        for code_point in unicode_string_input:
            try:
                acc_unicode_string += code_point.decode('UTF-8')
            except UnicodeDecodeError:
                # Skip invalid characters
                pass
        unicode_string_output = acc_unicode_string
    for replaced, replacer in replace_characters.iteritems():
        unicode_string_output = unicode_string_output.replace(replaced,
                                                              replacer)
    return unicode_string_output


class CSSToken(object):
    """The base class for all CSSToken objects.

    Parameters
    ----------
    string : str
        The string value of the token.
    """

    def __init__(self, string):
        self.value = string

    def __str__(self):
        return self.value

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        values_equal = (self.value == other.value)
        classes_equal = (type(self) == type(other))
        subclass_of = (issubclass(self, other) or issubclass(other, self))
        return values_equal and (classes_equal or subclass_of)


class WhitespaceToken(CSSToken):
    """A CSS Token representing an arbitrary amount of whitespace.

    Whitespace of any length or type is arbitrarily reduced to a single space.
    """

    def __init__(self):
        super(WhitespaceToken, self).__init__(' ')


class NumberToken(CSSToken):
    """A CSS Token representing some sort of number

    Parameters
    ----------
    string_repr : str
        The string representation of the number.
    numeric_value : int, float
        The numeric value of the number, either an integer or a floating point
        number depending on the type_flag.
    type_flag : str {'integer', 'number'}
        The type of number this NumberToken instance holds.
    """

    def __init__(self, string_repr, numeric_value, type_flag):
        self.string = string_repr
        self.value = numeric_value
        self.type_ = type_flag

    def __str__(self):
        return self.string


class DimensionToken(NumberToken):
    """A Number Token with a unit of measure.

    For example, `10px` is a number token measured in terms of pixels.

    Parameters
    ----------
    string_repr : str
        The string representation of the number.
    numeric_value : int, float
        The numeric value of the number, either an integer or a floating point
        number depending on the type_flag.
    type_flag : str {'integer', 'number'}
        The type of number this NumberToken instance holds.
    unit : str
        The unit of measure for this number token.  In the above example the
        unit is `px` or pixels.
    """

    def __init__(self, string_repr, numeric_value, type_flag, unit):
        super(DimensionToken, self).__init__(
            string_repr, numeric_value, type_flag)
        self.unit = unit

    def __str__(self):
        return "{} {}".format(super(DimensionToken, self).__str__(), self.unit)


class PercentageToken(NumberToken):
    """A Number Token that represents some percentage value.

    Parameters
    ----------
    string_repr : str
        The string representation of the number.
    numeric_value : int, float
        The numeric value of the number, either an integer or a floating point
        number depending on the type_flag.
    """

    def __init__(self, string_repr, numeric_value):
        super(PercentageToken, self).__init__(
            string_repr, numeric_value, 'number')

    def __str__(self):
        return "{} %".format(super(PercentageToken, self).__str__())


class IdentToken(CSSToken):
    """A CSS Token that represents an identifier.

    Parameters
    ----------
    name : str
        The name of the identifier.
    """

    def __init__(self, name):
        super(IdentToken, self).__init__(name)


class FunctionToken(IdentToken):
    """An identifier that specifically identifies a function.

    Parameters
    ----------
    name : str
        The name of the function.
    """

    def __init__(self, name):
        super(FunctionToken, self).__init__(name)


class URLToken(FunctionToken):
    """A token representing a URL function

    Parameters
    ----------
    value : str
        The value of the url function
    """

    def __init__(self, value):
        super(URLToken, self).__init__(value)


class LiteralToken(CSSToken):
    """A literal token.

    Used to represent the various string literals that are used to determine
    scope (among other things) within a CSS document.

    Parameters
    ----------
    value : str, { "{", "}", "[", "]", "(", ")", ";", ":", "," }
        The value of the string literal.
    """

    def __init__(self, value):
        super(LiteralToken, self).__init__(value)


class StringToken(CSSToken):
    """Token representing a string.

    Parameters
    ----------
    value : str
        The string held by the token.
    """

    def __init__(self, value):
        super(StringToken, self).__init__(value)


class BadStringToken(StringToken):
    """Token representing an invalid string.

    An invalid string is any string that contains an unescaped newline.  All
    `BadStringToken`s have a value of '', the empty string.
    """

    def __init__(self):
        super(BadStringToken, self).__init__('')


class HashToken(CSSToken):
    """A CSS Token representing an id selector.

    For example, #foo {} selects the id `foo`.

    Parameters
    ----------
    value : str
        The name being selected
    type_ : str, { 'unrestricted', 'id' }
        The type of the HashToken (what is being selected).
    """

    def __init__(self, value, type_):
        super(HashToken, self).__init__(value)
        self.type_flag = type_


class DelimToken(CSSToken):
    """Token used as a delimiter.

    Parameters
    ----------
    value : str
        The value of the delimiter.
    """

    def __init__(self, value):
        super(DelimToken, self).__init__(value)


class SuffixMatchToken(CSSToken):
    """Indicates a suffix match.  I don't actually know what this is yet..."""

    def __init__(self):
        super(SuffixMatchToken, self).__init__('')


class SubstringMatchToken(CSSToken):
    """Indicates a substring match.  I don't actually know what this is yet...
    """

    def __init__(self):
        super(SubstringMatchToken, self).__init__('')


class PrefixMatchToken(CSSToken):
    """Indicates a prefix match.  I don't actually know what this is yet..."""

    def __init__(self):
        super(PrefixMatchToken, self).__init__('')


class CDOToken(CSSToken):
    """Indicates a CDO Token.  Don't know what this is yet..."""

    def __init__(self):
        super(CDOToken, self).__init__('')


class CDCToken(CSSToken):
    """Indicates a CDC Token.  I don't actually know what this is yet..."""

    def __init__(self):
        super(CDCToken, self).__init__('')


class DashMatchToken(CSSToken):
    """Indicates a dash match.  I don't actually know what this is yet..."""

    def __init__(self):
        super(DashMatchToken, self).__init__('')


class IncludeMatchToken(CSSToken):
    """Indicates an include match.  I don't actually know what this is yet...
    """

    def __init__(self):
        super(IncludeMatchToken, self).__init__('')


class ColumnToken(CSSToken):
    """Indicates a column.  I don't actually know what this is yet..."""

    def __init__(self):
        super(ColumnToken, self).__init__('')


class AtKeywordToken(IdentToken):
    """An at rule.

    Parameters
    ----------
    value : str
        The name of the at rule.
    """

    def __init__(self, value):
        super(AtKeywordToken, self).__init__(value)


class CSSTokenizer(object):
    """Tokenizes a CSS string as per the W3C specifications[1]_.

    All regular expressions, string comparisons, etc are based on their unicode
    values as per the UTF-8 specification[2]_.

    .. [1] http://dev.w3.org/csswg/css-syntax/
    .. [2] https://tools.ietf.org/html/rfc3629

    Parameters
    ----------
    input_string : str
        The string containing the CSS to be tokenized.

    Attributes
    ----------
    stream
    tokens
    current_code_point
    next_code_point
    digit : _sre.SRE_Pattern
        Regular expression that matches digits 0-9.
    hex_digit : _sre.SRE_Pattern
        Regular expression that matches hex digits: 0-9, a-f, A-F.
    letter : _sre.SRE_Pattern
        Regular expression that matches all letters: a-z, A-Z.
    non_ascii : _sre.SRE_Pattern
        Regular expression that matches all non-ASCII code points, that is the
        code points with a value greater than U+007F.
    name_start : _sre.SRE_Pattern
        Regular expression that matches a "name-start" code point.  This
        includes all letters, non-ASCII code points, and the low line code
        point U+005F ( _ ).
    name : _sre.SRE_Pattern
        Regular expression that matches a "name" code point.  This includes
        any name-start code point, any digit, and the hyphen-minus code point
        U+002D (-).
    non_printable : _sre.SRE_Pattern
        Regular expression that matches so-called "non-printable" code points.
        This includes any code point between U+0000 NULL and U+0008 BACKSPACE,
        U+000B LINE TABULATION, any code point between U+000E SHIFT OUT and
        U+001F INFORMATION SEPARATOR ONE, or U+007F DELETE.
    newline : _sre.SRE_Pattern
        Regular expression that mathces U+000A LINE FEED. Note that U+000D
        CARRIAGE RETURN and U+000C FORM FEED are not included in this
        definition, as they are converted to U+000A LINE FEED during
        preprocessing.
    whitespace : _sre.SRE_Pattern
        Regular expression that matches any whitespace character.  Includes
        newlines, U+0009 CHARACTER TABULATION, and U+0020 SPACE.
    surrogate : _sre.SRE_Pattern
        Regular expression that matches so-called "surrogate" code points.
        This includes any code point between U+D800 and U+DFFF.
    quotations : _sre.SRE_Pattern
        Regular expression that matches either type of quote, U+0022 (") or
        U+0027 (').
    url : _sre.SRE_Pattern
        Regular expression that matches the word 'url' in a non-case sensitive
        manner.
    literal_tokens : list
        A list of the literal tokens used by CSS. This includes the values
        \u0028, \u0029, \u002C, \u003A, \u003B, \u005B, \u005D, \u007B, \u007D
    octothorpe : unicode
        The # code point U+0023.
    forward_slash : unicode
        The / code point U+002F.
    dollar_sign : unicode
        The $ code point U+0024.
    asterisk : unicode
        The * code point U+002A.
    plus : unicode
        The + code point U+002B.
    minus : unicode
        The - code point U+002D.
    full_stop : unicode
        The . code point U+002E.
    less_than : unicode
        The < code point U+003C.
    greater_than : unicode
        The > code point u+003E.
    equals_sign : unicode
        The = code point U+003D.
    at_sign : unicode
        The @ code point U+0040.
    backslash : unicode
        The \ code point U+005C.
    circumflex : unicode
        The ^ code point U+005E.
    vertical : unicode
        The | code point U+007C.
    tilde : unicode
        The ~ code point U+007E.
    percent : unicode
        The % code point U+0025.
    lparen : unicode
        The ( code point U+0028.
    rparen : unicode
        The ) code point U+0029.
    double_quote : unicode
        The " code point U+0022.
    single_quote : unicode
        The ' code point U+0027.
    exclamation_point : unicode
        The ! code point U+002D.
    EOF : types.NoneType
        Conceptual end of file.
    """

    digit = re.compile(u'[\u0030-\u0039]')
    hex_digit = re.compile(u'[\u0030-\u0039\u0041-\u0046\u0061-\u0066]')
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
    quotations = re.compile(u'[\u0022\u0027]')
    url = re.compile(u'url', re.IGNORECASE)
    literal_tokens = [u'\u0028', u'\u0029', u'\u002C', u'\u003A', u'\u003B',
                      u'\u005B', u'\u005D', u'\u007B', u'\u007D']
    octothorpe = u'\u0023'
    forward_slash = u'\u002F'
    dollar_sign = u'\u0024'
    asterisk = u'\u002A'
    plus = u'\u002B'
    minus = u'\u002D'
    full_stop = u'\u002E'
    less_than = u'\u003C'
    greater_than = u'\u003E'
    equals_sign = u'\u003D'
    at_sign = u'\u0040'
    backslash = u'\u005C'
    circumflex = u'\u005E'
    vertical = u'\u007C'
    tilde = u'\u007E'
    percent = u'\u0025'
    lparen = u'\u0028'
    rparen = u'\u0029'
    double_quote = u'\u0022'
    single_quote = u'\u0027'
    exclamation_point = u'\u002D'
    EOF = None

    _stream = None
    _tokens = None
    _current = None
    _next = ''

    @staticmethod
    def _valid_escape(first, second):
        """Determines whether two code points form a valid escape sequence.

        Parameters
        ----------
        first : unicode
            The first code point.
        second : unicode
            The second code point.

        Returns
        -------
        bool

        Notes
        -----
        The first code point must be a backslash and the second code point must
        not be a newline for this  method to return True.

        """
        if first == CSSTokenizer.backslash:
            if not CSSTokenizer.newline.match(second):
                return True
        return False

    @classmethod
    def _string_to_number(cls, string):
        """Converts a string to a number.

        Parameters
        ----------
        string : unicode
            The string to be converted.

        Returns
        -------
        int, float
            The value of the number

        Notes
        -----
        Divide the string into seven components, in order from left to right:
            Sign, integer part, decimal, fractional part, exponent indicator,
            exponent sign, exponent value.
        These are explained in the docstrings of the helper methods.

        Return a value s·(i + f·10-d)·10te.
        """

        sign, sign_removed = cls._get_sign(string)
        integer, int_removed = cls._get_integer(sign_removed)
        integer *= sign
        if int_removed:
            dec_removed = cls._get_decimal(int_removed)
            if dec_removed:
                fractional, frac_removed = cls._get_fractional(dec_removed)
                decimal_places = pow(10, -1*len(fractional))
                fractional = int(fractional) * sign
                if frac_removed:
                    exponent = pow(10, cls._get_exponent(frac_removed))
                    return (integer + fractional*decimal_places) * exponent
                else:
                    return float(integer + (fractional * decimal_places))
            else:
                return float(integer)
        else:
            return integer

    @classmethod
    def _get_sign(cls, string):
        """Determines the sign of a string number.

        Sign is determined by a single U+002B PLUS SIGN (+) or U+002D
        HYPHEN-MINUS (-) or the empty string. Let s be the number -1 if the
        sign is U+002D HYPHEN-MINUS (-); otherwise, let s be the number 1.

        Parameters
        ----------
        string : unicode
            The number whose sign needs to be determined.

        Returns
        -------
        tuple
            Returns a tuple, the first value is the sign (-1 or 1) and the
            second value is the optionally truncated string that needs further
            parsing.
        """

        if string[0] == cls.minus:
            return -1, string[1:]
        elif string[0] == cls.plus:
            return 1, string[1:]
        else:
            return 1, string

    @classmethod
    def _get_integer(cls, string):
        """Determines the integer part of a number in string form.

        The integer part consists of zero or more digits. If there is at least
        one digit, let i be the number formed by interpreting the digits as a
        base-10 integer; otherwise, let i be the number 0.

        Parameters
        ----------
        string : unicode
            The string whose integer part is to be determined

        Returns
        -------
        tuple
            A tuple of form (number, string) where the number is the integer
            part and the string is the remaining string to be parsed.
        """

        integer = ''
        while string:
            char = string[0]
            if cls.digit.match(char):
                integer += char
                string = string[1:]
            else:
                break
        try:
            return int(integer), string
        except ValueError:
            return 0, string

    @classmethod
    def _get_decimal(cls, string):
        """Determines whether or not a decimal point (and thus fractional
        portion) is present in the number.

        Determined by a single U+002E FULL STOP (.), or the empty string.

        Parameters
        ----------
        string : unicode
            The string to be parsed

        Returns
        -------
        unicode
            The remaining string to be parsed.
        """

        if string:
            if string[0] == cls.full_stop:
                return string[1:]
            else:
                return string

    @classmethod
    def _get_fractional(cls, string):
        """Gets the fractional portion of a number.

        A fractional part: zero or more digits. If there is at least one digit,
        let f be the number formed by interpreting the digits as a base-10
        integer and d be the number of digits; otherwise, let f and d be the
        number 0.  The number of digits is calculated by whatever calls this
        function.

        Parameters
        ----------
        string : unicode
            The string to be parsed.

        Returns
        -------
        tuple
            Returns a tuple of form (string, string).  The first string is the
            fractional portion in string form, and the second is the remaining
            string to be parsed.
        """

        fractional = '0'
        leftover_string = ''
        i = 0
        for i in range(len(string)):
            char = string[i]
            if cls.digit.match(char):
                fractional = fractional.lstrip('0')
                fractional += char
            else:
                break
        if i < len(string)-1:
            leftover_string = string[i:]
        return fractional, leftover_string

    @classmethod
    def _get_exponent(cls, string):
        """Calculates the exponential portion of a string.

        Consists of an exponent indicator, an exponent sign, and the exponent
        value.

        Parameters
        ----------
        string : unicode
            The string to be parsed

        Returns
        -------
        int
            The value of the exponential portion.

        Notes
        -----
        An exponent indicator: a single U+0045 LATIN CAPITAL LETTER E (E) or
        U+0065 LATIN SMALL LETTER E (e), or the empty string.

        An exponent sign: a single U+002B PLUS SIGN (+) or U+002D HYPHEN-MINUS
        (-), or the empty string. Let t be the number -1 if the sign is U+002D
        HYPHEN-MINUS (-); otherwise, let t be the number 1.

        An exponent: zero or more digits. If there is at least one digit let e
        be the number formed by interpreting the digits as a base-10 integer;
        otherwise, let e be the number 0.
        """

        if string[0] in ['e', 'E']:
            try:
                if string[1] == cls.minus:
                    return -1 * int(string[2:])
                elif string[1] == cls.plus:
                    return int(string[2:])
                else:
                    return int(string[1:])
            except IndexError:
                return 0
        return 0

    def __init__(self, input_string):
        self.tokens = deque()
        self.stream = input_string
        self.current_code_point = ''
        self.next_code_point = self.stream

    @property
    def stream(self):
        """The byte stream of unicode code points that is to be tokenized"""

        return self._stream

    @stream.setter
    def stream(self, value):
        self._stream = deque(preprocessing(value))

    @property
    def tokens(self):
        """The stream of tokens that have been processed"""

        return self._tokens

    @tokens.setter
    def tokens(self, iterable):
        if self._tokens is None:
            self._tokens = deque()
        self._tokens.extend(iterable)

    @property
    def current_code_point(self):
        """The current code point that is being considered by the tokenizer"""

        return self._current

    @current_code_point.setter
    def current_code_point(self, new_code_point):
        self._current = new_code_point

    @property
    def next_code_point(self):
        """The next code point to be considered by the tokenizer"""

        return self._next

    @next_code_point.setter
    def next_code_point(self, stream):
        try:
            self._next = stream[0]
        except IndexError:
            self._next = CSSTokenizer.EOF

    def tokenize_stream(self):
        """Tokenizes the code points within the byte stream.  Calls utility
        methods to handle the various different tokenization algorithms
        """

        while self.stream:
            if self.next_code_point is None:
                break
            self.consume_next_code_point()
            if self.current_code_point == CSSTokenizer.forward_slash:
                self.consume_comment()
            elif CSSTokenizer.whitespace.match(self.current_code_point):
                self.consume_whitespace_token()
            elif CSSTokenizer.digit.match(self.current_code_point):
                self.consume_numeric_token()
            elif self.current_code_point == CSSTokenizer.plus:
                self.handle_plus_sign()
            elif self.current_code_point == CSSTokenizer.minus:
                self.handle_minus_sign()
            elif self.current_code_point == CSSTokenizer.full_stop:
                self.handle_period()
            elif CSSTokenizer.name_start.match(self.current_code_point):
                self.consume_ident_like_token()
            elif self.current_code_point in CSSTokenizer.literal_tokens:
                self.consume_literal_token()
            elif CSSTokenizer.quotations.match(self.current_code_point):
                self.consume_string_token()
            elif self.current_code_point == CSSTokenizer.octothorpe:
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
            elif self.current_code_point == CSSTokenizer.at_sign:
                self.consume_commercial_at_token()
            elif self.current_code_point == CSSTokenizer.tilde:
                self.consume_include_match_token()
            else:
                self.consume_delim_token()

    def lookahead(self, distance):
        """Peeks along the byte stream to check what the next several code
        points will be.

        Parameters
        ----------
        distance : int
            How many code points ahead to peek at.

        Returns
        -------
        list
            The next `distance` values to look at.  Uses `None` as a
            placeholder if there are no more values to look at.
        """

        peek = []
        for i in range(distance):
            try:
                peek.append(self.stream[i])
            except IndexError:
                peek.append(None)
        return peek

    def consume_next_code_point(self):
        """Consumes the next code point in the stream and assigns the next
        code point.
        """

        self._consume_n_code_points(1)
        # self.current_code_point = self.stream.popleft()
        # self.next_code_point = self.stream

    def _consume_n_code_points(self, n):
        """Consumes an arbitrary number of code points, if possible."""

        for _ in range(n):
            try:
                self.current_code_point = self.stream.popleft()
                self.next_code_point = self.stream
            except IndexError:
                break

    def reconsume_current_code_point(self):
        """Pushes the current code point onto the front of the stream."""

        self.stream.appendleft(self.current_code_point)
        self.current_code_point = None
        self.next_code_point = self.stream

    def _starts_identifier(self):
        """Determines whether or not the current code point and the next two
        code points start an identifier.

        Notes
        -----
        Look at the first code point:

           | - U+002D HYPHEN-MINUS
           |     If the second code point is a name-start code point or a
           |     U+002D HYPHEN-MINUS, or the second and third code points are a
           |     valid escape, return true. Otherwise, return false.
           | - name-start code point
           |     Return true.
           | - U+005C REVERSE SOLIDUS (\)
           |     If the first and second code points are a valid escape, return
           |     true. Otherwise, return false.
           | - anything else
           |     Return false.
        """

        first, second, third = self.lookahead(3)
        if first is CSSTokenizer.EOF:
            return False
        elif first == CSSTokenizer.minus:
            if second is CSSTokenizer.EOF:
                return False
            elif CSSTokenizer.name_start.match(second):
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

    def consume_comment(self):
        """Consumes comments within a CSS document but does not store the
        information within them anywhere.

        Notes
        -----
        If the next two input code point are U+002F SOLIDUS (/) followed by a
        U+002A ASTERISK (*), consume them and all following code points up to
        and including the first U+002A ASTERISK (*) followed by a U+002F
        SOLIDUS (/), or up to an EOF code point. Return to the start of this
        step.
        """
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
        """Consumes an arbitrary amount of whitespace of arbitrary type.  Adds
        a WhitespaceToken to the end of the list of tokens.
        """

        self.tokens.append(WhitespaceToken())
        while (self.next_code_point is not None and
                CSSTokenizer.whitespace.match(self.next_code_point)):
            self.consume_next_code_point()

    def _consume_digits(self):
        """Consumes numeric strings and returns them for further parsing.

        Returns
        -------
        digit_string : unicode
            String representing a series of numbers.
        """

        digit_string = u''
        if CSSTokenizer.digit.match(self.current_code_point):
            digit_string += self.current_code_point
        if self.next_code_point is not None:
            while CSSTokenizer.digit.match(self.next_code_point):
                self.consume_next_code_point()
                digit_string += self.current_code_point
                if self.next_code_point is None:
                    break
        return digit_string

    def _consume_number(self):
        """Consumes a number.

        Returns
        -------
        tuple
            A 3-member tuple.  The first value is a string representation of
            the number, the second is the numeric value, and the last is the
            type (integer or not) of the number.
        """

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

        numeric_value = CSSTokenizer._string_to_number(string_representation)

        return string_representation, numeric_value, type_flag

    def consume_numeric_token(self):
        """Consumes a numeric token: PercentageToken, DimensionToken, or
        NumberToken.
        """

        string_repr, numeric_value, type_flag = self._consume_number()
        if self.next_code_point == CSSTokenizer.percent:
            self.consume_next_code_point()
            self.tokens.append(PercentageToken(string_repr, numeric_value))
        else:
            if self.next_code_point is not None:
                self.consume_next_code_point()
                if self._starts_identifier():
                    name = self._consume_name()
                    self.tokens.append(DimensionToken(
                        string_repr, numeric_value, type_flag, name))
            else:
                self.tokens.append(
                    NumberToken(string_repr, numeric_value, type_flag))

    def handle_plus_sign(self):
        """Handles the case where the current code point is U+002B PLUS SIGN.

        If the input stream starts with a number, reconsume the current input
        code point, consume a numeric token and return it.  Otherwise, return a
        <delim-token> with its value set to the current input code point.
        """

        if self.next_code_point is not CSSTokenizer.EOF:
            if CSSTokenizer.digit.match(self.next_code_point):
                self.consume_numeric_token()
                return
        self.consume_delim_token()

    def handle_minus_sign(self):
        """Handles the case where the current code point is U+002D HYPHEN-MINUS
        (-).

        If the input stream starts with a number, reconsume the current input
        code point, consume a numeric token, and return it.

        Otherwise, if the next 2 input code points are U+002D HYPHEN-MINUS
        U+003E GREATER-THAN SIGN (->), consume them and return a <CDC-token>.

        Otherwise, if the input stream starts with an identifier, reconsume the
        current input code point, consume an ident-like token, and return it.

        Otherwise, return a <delim-token> with its value set to the current
        input code point.
        """

        if self.next_code_point is not CSSTokenizer.EOF:
            if CSSTokenizer.digit.match(self.next_code_point):
                self.consume_numeric_token()
                return
            elif self.lookahead(2) == [CSSTokenizer.minus,
                                       CSSTokenizer.greater_than]:
                self.consume_CDC_token()
                return
            self.consume_next_code_point()
            if self._starts_identifier():
                self.reconsume_current_code_point()
                self.stream.appendleft(u'\u002D')
                self.consume_ident_like_token()
                return
        self.reconsume_current_code_point()
        self.current_code_point = u'\u002D'
        self.consume_delim_token()

    def handle_period(self):
        """Handles the case where the current code point is a U+002E FULL STOP.

        If the input stream starts with a number, reconsume the current input
        code point, consume a numeric token, and return it.

        Otherwise, return a <delim-token> with its value set to the current
        input code point.
        """

        if self.next_code_point is not CSSTokenizer.EOF:
            if CSSTokenizer.digit.match(self.next_code_point):
                self.stream.extendleft('.0')   # extendleft reverses the order
                self.consume_numeric_token()
                return
        self.consume_delim_token()

    def _consume_name(self):
        result = ''
        if self.current_code_point is not CSSTokenizer.EOF:
            if CSSTokenizer.name.match(self.current_code_point):
                result += self.current_code_point
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
        name = self._consume_name()
        next_is_lparen = (self.next_code_point == CSSTokenizer.lparen)
        if CSSTokenizer.url.match(name) and next_is_lparen:
            self.consume_next_code_point()
            first, second = self.lookahead(2)
            if first is None:
                self.consume_url_token()
                return
            elif second is None:
                if CSSTokenizer.quotations.match(first):
                    self.tokens.append(FunctionToken(name))
                    return
                else:
                    self.consume_url_token()
            while (CSSTokenizer.whitespace.match(first) and
                   CSSTokenizer.whitespace.match(second)):
                self.consume_next_code_point()

            if ((CSSTokenizer.whitespace.match(first) and
                    CSSTokenizer.quotations.match(second)) or
                    (CSSTokenizer.quotations.match(first))):
                self.tokens.append(FunctionToken(name))
            else:
                self.consume_url_token()
        elif next_is_lparen:
            self.consume_next_code_point()
            self.tokens.append(FunctionToken(name))
        self.tokens.append(IdentToken(name))

    def consume_url_token(self):
        result = ''
        while CSSTokenizer.whitespace.match(self.next_code_point):
            self.consume_next_code_point()
        if self.next_code_point is None:
            self.tokens.append(URLToken(result))
        else:
            while self.stream:
                self.consume_next_code_point()
                if (self.current_code_point == CSSTokenizer.rparen or
                        self.next_code_point is None):
                    break
                elif (self.current_code_point == CSSTokenizer.lparen or
                      CSSTokenizer.quotations.match(self.current_code_point) or
                      CSSTokenizer.non_printable.match(
                        self.current_code_point)):
                    # This is a parse error
                    self.consume_bad_url_token()
                    return
                elif self.current_code_point == CSSTokenizer.backslash:
                    if self._valid_escape(self.current_code_point,
                                          self.next_code_point):
                        result += self.consume_escape_token()
                    else:
                        # This is a parse error
                        self.consume_bad_url_token()
                        return
                else:
                    result += self.current_code_point
            self.tokens.append(URLToken(result))

    def consume_bad_url_token(self):
        while self.stream:
            try:
                self.consume_next_code_point()
            except IndexError:
                break
            else:
                if self.current_code_point == ')':
                    break
                elif self._valid_escape(self.current_code_point,
                                        self.next_code_point):
                    self.consume_escape_token()
                else:
                    pass
        return

    def consume_literal_token(self):
        self.tokens.append(LiteralToken(self.current_code_point))

    def consume_string_token(self):
        result = ''
        if self.current_code_point == CSSTokenizer.double_quote:
            end_code_point = CSSTokenizer.double_quote
        else:
            end_code_point = CSSTokenizer.single_quote

        try:
            self.consume_next_code_point()
        except IndexError:   # EOF
            self.tokens.append(StringToken(result))
        else:
            while self.stream:
                self.consume_next_code_point()
                if self.current_code_point == end_code_point:
                    break
                elif CSSTokenizer.newline.match(self.current_code_point):
                    # This is a parse error
                    self.reconsume_current_code_point()
                    self.tokens.append(BadStringToken())
                    return
                elif self.current_code_point == CSSTokenizer.backslash:
                    if self.next_code_point is None:
                        break
                    elif CSSTokenizer.newline.match(self.next_code_point):
                        self.consume_next_code_point()
                    else:
                        result += self.consume_escape_token()
                else:
                    result += self.current_code_point
            self.tokens.append(StringToken(result))

    def consume_hash_token(self):
        type_flag = 'unrestricted'
        peek = self.lookahead(2)
        valid_escape = self._valid_escape(*peek)
        if CSSTokenizer.name.match(self.next_code_point) or valid_escape:
            if self._starts_identifier():
                type_flag = 'id'
            name = self._consume_name()
            self.tokens.append(HashToken(name, type_flag))
        else:
            self.consume_delim_token()

    def consume_prefix_match_token(self):
        if self.next_code_point == CSSTokenizer.equals_sign:
            self.consume_next_code_point()
            self.tokens.append(PrefixMatchToken())
        else:
            self.consume_delim_token()

    def consume_suffix_match_token(self):
        if self.next_code_point == CSSTokenizer.equals_sign:
            self.consume_next_code_point()
            self.tokens.append(SuffixMatchToken())
        else:
            self.consume_delim_token()

    def consume_substring_match_token(self):
        if self.next_code_point == CSSTokenizer.equals_sign:
            self.consume_next_code_point()
            self.tokens.append(SubstringMatchToken())

    def consume_CDO_token(self):
        if self.lookahead(3) == [CSSTokenizer.exclamation_point,
                                 CSSTokenizer.minus,
                                 CSSTokenizer.minus]:
            self.consume_next_code_point()
            self.consume_next_code_point()
            self.consume_next_code_point()
            self.tokens.append(CDOToken())
        else:
            self.consume_delim_token()

    def consume_CDC_token(self):
        self.consume_next_code_point()
        self.consume_next_code_point()
        self.tokens.append(CDCToken())

    def consume_escape_token(self):
        try:
            self.consume_next_code_point()
        except IndexError:   # EOF
            return replacement_character
        else:
            if CSSTokenizer.hex_digit.match(self.current_code_point):
                hex_string = self.current_code_point
                while (CSSTokenizer.hex_digit.match(self.current_code_point)and
                       len(hex_string) <= 6):
                    try:
                        self.consume_next_code_point()
                    except IndexError:   # empty deque
                        break
                    else:
                        hex_string += self.current_code_point
                hex_number = int(hex_string, 16)
                surrogate = CSSTokenizer.surrogate.match(unichr(hex_number))
                invalid_code_point = hex_number > int("10FFFF", 16)
                if hex_number == 0 or surrogate or invalid_code_point:
                    return replacement_character
                else:
                    return str(hex_number)
            else:
                if self.current_code_point is not CSSTokenizer.EOF:
                    return self.current_code_point
                else:
                    return replacement_character

    def consume_dash_match_token(self):
        if self.next_code_point == CSSTokenizer.equals_sign:
            self.consume_next_code_point()
            self.tokens.append(DashMatchToken())
        elif self.next_code_point == CSSTokenizer.vertical:
            self.consume_next_code_point()
            self.tokens.append(ColumnToken())
        else:
            self.consume_delim_token()

    def consume_include_match_token(self):
        if self.next_code_point == CSSTokenizer.equals_sign:
            self.consume_next_code_point()
            self.tokens.append(IncludeMatchToken())
        else:
            self.consume_delim_token()

    def consume_delim_token(self):
        self.tokens.append(DelimToken(self.current_code_point))

    def consume_commercial_at_token(self):
        if self._starts_identifier():
            name = self._consume_name()
            self.tokens.append(AtKeywordToken(name))
        else:
            self.consume_delim_token()
