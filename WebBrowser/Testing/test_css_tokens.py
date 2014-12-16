# -*- coding: utf-8 -*-
# Implemented as per http://dev.w3.org/csswg/css-syntax/#tokenizing-and-parsing

from nose.plugins.skip import SkipTest

from WebBrowser.parser.tokens.css_tokens import CSS_tokens, preprocessing


class test_comment_token(object):

    regex = CSS_tokens["<comment-token>"]

    def test_single_line_comment(self):
        input = preprocessing("/* Hello, I am a comment */")
        assert self.regex.match(input)

    def test_multiline_comment(self):
        input = preprocessing("""/* Hello, I am a
        multiline
        comment
        */""")
        assert self.regex.match(input)

    def test_bad_single_line_comment(self):
        input = preprocessing("/* Hello, I am a bad single line comment")
        assert self.regex.match(input) is None

    def test_bad_multiline_comment(self):
        input = preprocessing("""/* Hello, I am a bad
        multiline
        comment
        """)
        assert self.regex.match(input) is None


class test_newline_token(object):
    regex = CSS_tokens['<newline-token>']

    def test_good_newline1(self):
        input = preprocessing("""\n""")
        assert self.regex.match(input)

    def test_good_newline2(self):
        input = preprocessing("""\r""")
        assert self.regex.match(input)

    def test_good_newline3(self):
        input = preprocessing("""\f""")
        assert self.regex.match(input)

    def test_good_newline4(self):
        input = preprocessing("""\r\n""")
        assert self.regex.match(input)

    def test_bad_newline(self):
        input = preprocessing("""f\n""")
        assert self.regex.match(input) is None


class test_whitespace_token(object):
    regex = CSS_tokens["<whitespace-token>"]

    def test_good_whitespace1(self):
        input = preprocessing("""\n""")
        assert self.regex.match(input)

    def test_good_whitespace2(self):
        input = preprocessing("""\r""")
        assert self.regex.match(input)

    def test_good_whitespace3(self):
        input = preprocessing("""\f""")
        assert self.regex.match(input)

    def test_good_whitespace4(self):
        input = preprocessing("""\r\n""")
        assert self.regex.match(input)

    def test_good_whitespace5(self):
        input = preprocessing(""" """)
        assert self.regex.match(input)

    def test_good_whitespace6(self):
        input = preprocessing("""\t""")
        assert self.regex.match(input)

    def test_good_whitespace7(self):
        input = preprocessing("""    """)
        assert self.regex.match(input)

    def test_bad_whitespace(self):
        input = preprocessing("""sdfaef\nasdf""")
        assert self.regex.match(input) is None


class test_hex_digit_token(object):
    regex = CSS_tokens["<hex-digit-token>"]

    def test_good_hex_digit1(self):
        input = preprocessing("""0""")
        assert self.regex.match(input)

    def test_good_hex_digit2(self):
        input = preprocessing("""a""")
        assert self.regex.match(input)

    def test_good_hex_digit3(self):
        input = preprocessing("""A""")
        assert self.regex.match(input)

    def test_good_hex_digit4(self):
        input = preprocessing("""9""")
        assert self.regex.match(input)

    def test_bad_hex_digit1(self):
        input = preprocessing("""10""")
        assert self.regex.match(input) is None

    def test_bad_hex_digit2(self):
        input = preprocessing("""L""")
        assert self.regex.match(input) is None


class test_escape_token(object):
    regex = CSS_tokens["<escape-token>"]

    def test_good_escape1(self):
        input = preprocessing(r"""\z""")
        assert self.regex.match(input)

    def test_good_escape2(self):
        input = preprocessing(r"""\7 """)
        assert self.regex.match(input)

    def test_good_escape3(self):
        input = preprocessing(r"""\!""")
        assert self.regex.match(input)

    def test_bad_escape1(self):
        input = preprocessing(r"""\!a""")
        assert self.regex.match(input) is None

    def test_bad_escape2(self):
        input = preprocessing("""\na""")
        assert self.regex.match(input) is None

    def test_bad_escape3(self):
        input = preprocessing(r"""\aa""")
        assert self.regex.match(input) is None


class test_ident_token(object):
    regex = CSS_tokens["<ident-token>"]

    @classmethod
    def setup_class(cls):
        # Haven't written it yet
        raise SkipTest

    def test_good_ident1(self):
        input = preprocessing("""--""")
        assert self.regex.match(input)

    def test_good_ident2(self):
        input = preprocessing("""--asdl_-fiu""")
        assert self.regex.match(input)

    def test_good_ident3(self):
        input = preprocessing("""--�""")
        assert self.regex.match(input)

    def test_good_ident4(self):
        input = preprocessing("""--\z""")
        assert self.regex.match(input)

    def test_good_ident5(self):
        input = preprocessing("""asdl_fiu""")
        assert self.regex.match(input)

    def test_good_ident6(self):
        input = preprocessing("""-asdl_-fiu""")
        assert self.regex.match(input)

    def test_good_ident7(self):
        input = preprocessing("""�""")
        assert self.regex.match(input)

    def test_good_ident8(self):
        input = preprocessing("""-�""")
        assert self.regex.match(input)

    def test_good_ident9(self):
        input = preprocessing("""-\z""")
        assert self.regex.match(input)

    def test_good_ident10(self):
        input = preprocessing("""\z""")
        assert self.regex.match(input)

    def test_bad_ident1(self):
        input = preprocessing("""--!""")
        a = self.regex.match(input)
        print a.groups()
        assert self.regex.match(input) is None

    def test_bad_ident2(self):
        input = preprocessing("""!""")
        assert self.regex.match(input) is None

    def test_bad_ident3(self):
        input = preprocessing("""-!""")
        a = self.regex.match(input)
        print a.groups()
        assert self.regex.match(input) is None


class test_function_token(object):
    regex = CSS_tokens["<function-token>"]

    def test_good_function1(self):
        input = preprocessing("""--(""")
        assert self.regex.match(input)

    def test_good_function2(self):
        input = preprocessing("""--asdl_-fiu(""")
        assert self.regex.match(input)

    def test_good_function3(self):
        input = preprocessing("""--�(""")
        assert self.regex.match(input)

    def test_good_function4(self):
        input = preprocessing("""--\z(""")
        assert self.regex.match(input)

    def test_good_function5(self):
        input = preprocessing("""asdl_fiu(""")
        assert self.regex.match(input)

    def test_good_function6(self):
        input = preprocessing("""-asdl_-fiu(""")
        assert self.regex.match(input)

    def test_good_function7(self):
        input = preprocessing("""�(""")
        assert self.regex.match(input)

    def test_good_function8(self):
        input = preprocessing("""-�(""")
        assert self.regex.match(input)

    def test_good_function9(self):
        input = preprocessing("""-\z(""")
        assert self.regex.match(input)

    def test_good_function10(self):
        input = preprocessing("""\z(""")
        assert self.regex.match(input)

    def test_bad_function1(self):
        input = preprocessing("""--a""")
        assert self.regex.match(input) is None

    def test_bad_function2(self):
        input = preprocessing("""a""")
        assert self.regex.match(input) is None

    def test_bad_function3(self):
        input = preprocessing("""-a""")
        assert self.regex.match(input) is None


class test_at_keyword_token(object):
    regex = CSS_tokens["<at-keyword-token>"]

    def test_good_at_keyword1(self):
        input = preprocessing("""@--""")
        assert self.regex.match(input)

    def test_good_at_keyword2(self):
        input = preprocessing("""@--asdl_-fiu""")
        assert self.regex.match(input)

    def test_good_at_keyword3(self):
        input = preprocessing("""@--�""")
        assert self.regex.match(input)

    def test_good_at_keyword4(self):
        input = preprocessing("""@--\z""")
        assert self.regex.match(input)

    def test_good_at_keyword5(self):
        input = preprocessing("""@asdl_fiu""")
        assert self.regex.match(input)

    def test_good_at_keyword6(self):
        input = preprocessing("""@-asdl_-fiu""")
        assert self.regex.match(input)

    def test_good_at_keyword7(self):
        input = preprocessing("""@�""")
        assert self.regex.match(input)

    def test_good_at_keyword8(self):
        input = preprocessing("""@-�""")
        assert self.regex.match(input)

    def test_good_at_keyword9(self):
        input = preprocessing("""@-\z""")
        assert self.regex.match(input)

    def test_good_at_keyword10(self):
        input = preprocessing("""@\z""")
        assert self.regex.match(input)

    def test_bad_at_keyword1(self):
        input = preprocessing("""a""")
        assert self.regex.match(input) is None

    def test_bad_at_keyword2(self):
        input = preprocessing("""a""")
        assert self.regex.match(input) is None

    def test_bad_at_keyword3(self):
        input = preprocessing("""a""")
        assert self.regex.match(input) is None


class test_hash_token(object):
    regex = CSS_tokens["<hash-token>"]

    def test_good_hash1(self):
        input = preprocessing("""#asdl_-fiu""")
        assert self.regex.match(input)

    def test_good_hash2(self):
        input = preprocessing("""#�""")
        assert self.regex.match(input)

    def test_good_hash3(self):
        input = preprocessing("""#\z""")
        assert self.regex.match(input)

    def test_bad_hash1(self):
        input = preprocessing("""asdl_-fiu""")
        assert self.regex.match(input) is None

    def test_bad_hash2(self):
        input = preprocessing("""�""")
        assert self.regex.match(input) is None

    def test_bad_hash3(self):
        input = preprocessing("""\z""")
        assert self.regex.match(input) is None


class test_string_token(object):
    regex = CSS_tokens["<string-token>"]

    def test_good_string1(self):
        input = preprocessing('''"asdf"''')
        assert self.regex.match(input)

    def test_good_string2(self):
        input = preprocessing("""'asdf'""")
        assert self.regex.match(input)

    def test_good_string3(self):
        input = preprocessing("""''""")
        assert self.regex.match(input)

    def test_good_string4(self):
        input = preprocessing('''""''')
        assert self.regex.match(input)

    def test_good_string5(self):
        input = preprocessing("""'as\'df'""")
        assert self.regex.match(input)

    def test_good_string6(self):
        input = preprocessing('''"as\"df"''')
        assert self.regex.match(input)

    def test_good_string7(self):
        input = preprocessing("""'as\\df'""")
        assert self.regex.match(input)

    def test_good_string8(self):
        input = preprocessing('''"as\\df"''')
        assert self.regex.match(input)

    def test_good_string9(self):
        input = preprocessing("""'as\\ndf'""")
        assert self.regex.match(input)

    def test_good_string10(self):
        input = preprocessing('''"as\\ndf"''')
        assert self.regex.match(input)

    def test_bad_string1(self):
        input = preprocessing('''"asdf\'''')
        assert self.regex.match(input) is None

    def test_bad_string2(self):
        input = preprocessing("""'asdf\"""")
        assert self.regex.match(input) is None

    def test_bad_string3(self):
        input = preprocessing("""'as'df'""")
        assert self.regex.match(input) is None

    def test_bad_string4(self):
        input = preprocessing('''"as"df"''')
        assert self.regex.match(input) is None

    def test_bad_string5(self):
        input = preprocessing("""'as\df'""")
        assert self.regex.match(input) is None

    def test_bad_string6(self):
        input = preprocessing('''"as\df"''')
        assert self.regex.match(input) is None

    def test_bad_string7(self):
        input = preprocessing("""'as\ndf'""")
        assert self.regex.match(input) is None

    def test_bad_string8(self):
        input = preprocessing('''"as\ndf"''')
        assert self.regex.match(input) is None


class test_url_token(object):
    regex = CSS_tokens["<url-token>"]

    @classmethod
    def setup_class(cls):
        # Haven't written it yet
        raise SkipTest

    def test_good_url1(self):
        input = preprocessing('''url()''')
        assert self.regex.match(input)

    def test_good_url2(self):
        input = preprocessing("""url(   \t)""")
        assert self.regex.match(input)

    def test_good_url3(self):
        input = preprocessing("""url(\n)""")
        assert self.regex.match(input)

    def test_good_url4(self):
        input = preprocessing('''"url(asdkgjhdf/   )"''')
        assert self.regex.match(input)

    def test_good_url5(self):
        input = preprocessing("""url(   asdkgjhdf/   )""")
        assert self.regex.match(input)

    def test_good_url6(self):
        input = preprocessing('''url(  asdkgjhdf/)''')
        assert self.regex.match(input)

    def test_good_url7(self):
        input = preprocessing("""url(asdkg\zjhdf/   )""")
        assert self.regex.match(input)

    def test_good_url8(self):
        input = preprocessing('''url(    asdkg\zjhdf/   )''')
        assert self.regex.match(input)

    def test_good_url9(self):
        input = preprocessing("""    url(asdkg\zjhdf)""")
        assert self.regex.match(input)

    def test_bad_url1(self):
        input = preprocessing('''url(\)''')
        assert self.regex.match(input) is None

    def test_bad_url2(self):
        input = preprocessing("""url( \  \t)""")
        assert self.regex.match(input) is None

    def test_bad_url3(self):
        input = preprocessing("""url(\/n)""")
        assert self.regex.match(input) is None

    def test_bad_url4(self):
        input = preprocessing('''"url(\asdkgjhdf/   )"''')
        assert self.regex.match(input) is None

    def test_bad_url5(self):
        input = preprocessing("""url(   \asdkgjhdf/   )""")
        assert self.regex.match(input) is None

    def test_bad_url6(self):
        input = preprocessing('''url(  \asdkgjhdf/)''')
        assert self.regex.match(input) is None

    def test_bad_url7(self):
        input = preprocessing("""url(\asdkg\zjhdf/   )""")
        assert self.regex.match(input) is None

    def test_bad_url8(self):
        input = preprocessing('''url(    \asdkg\zjhdf/   )''')
        assert self.regex.match(input) is None

    def test_bad_url9(self):
        input = preprocessing("""    url(\asdkg\zjhdf)""")
        assert self.regex.match(input) is None

