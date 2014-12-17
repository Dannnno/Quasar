import os


test_page_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_pages')


class test_small_css(object):

    @classmethod
    def setup_class(cls):
        cls.css_file = open(os.path.join(test_page_directory, 'small.css'), 'r')
        cls.css_text = preprocessing(cls.css_file.read())
        cls.tokenizer = CSSTokenizer(cls.css_text)

    @classmethod
    def teardown_class(cls):
        cls.css_file.close()