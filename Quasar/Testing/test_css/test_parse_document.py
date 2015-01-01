class TestSmallCSS1(object):

    @classmethod
    def setup_class(cls):
        cls.css = """#gbar,#guser {
    font-size : 13px;
    padding-top : 1px !important;
}"""