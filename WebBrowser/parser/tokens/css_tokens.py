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
from collections import OrderedDict
import re

replace_characters = OrderedDict()
line_feed = u'u\000F' # Line Feed
replacement_character = u'\uFFFD'
replace_characters[u'u\000Du\000F'] = line_feed   # Carriage Return + Line Feed
replace_characters[u'u\000D'] = line_feed   # Carriage Return (CR)
replace_characters[u'u\000C'] = line_feed   # Form Feed (FF)
replace_characters[u'u\0000'] = replacement_character


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
                                      #[(?P=<quote>)]\Z  # which we started with
                                           """, re.VERBOSE),

                                   #   ([^(?P=<quote>)\\\n\r\f]   # strings, but not multiline
                                   #    |
                                   #    \\\\([^a-fA-F0-9\r\n\f]\Z)|([a-fA-F0-9](?:\Z|\s))   # Escape token below
                                   #    |
                                   #    \\\\[\n\r\f]|\\\\\r\n   # Collecting escaped newlines
                                   #   )*
                                   #   [(?P=<quote>)]   # which we started with
              "<bad-string-token>": None,
              "<url-token>": re.compile("""
                                       url   # starts with url
                                       \(   # lparen
                                        \s*   # optional whitespace
                                        ([^"'\(\)\\\s]   #not quotes,
                                         |
                                         (\\([^a-fA-F0-9\r\n\f]\Z)|([a-fA-F0-9](?:\Z|\s)))  # Escape token below
                                        \s*   # optional whitespace
                                       \)   # endparen
                                        """, re.VERBOSE),
              "<bad-url-token>": None,
              "<delim-token>": None,
              "<number-token>": None,
              "<percentage-token>": None,
              "<dimension-token>": None,
              "<include-match-token>": None,
              "<dash-match-token>": None,
              "<prefix-match-token>": None,
              "<suffix-match-token>": None,
              "<substring-match-token>": None,
              "<column-token>": None,
              "<whitespace-token>": re.compile('\s+'),
              "<CDO-token>": None,
              "<CDC-token>": None,
              "<colon-token>": re.compile(r':'),
              "<semicolon-token>": re.compile(r';'),
              "<comma-token>": re.compile(r','),
              "<[-token>": re.compile(r'\['),
              "<]-token>": re.compile(r'\]'),
              "<(-token>": re.compile(r'\('),
              "<)-token>": re.compile(r'\)'),
              "<{-token>": re.compile(r'{'),
              "<}-token>.": re.compile(r'}'),
              # Below this are not real, official tokens from the site.
              # Just practice spaces for portions of the other regexes
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
