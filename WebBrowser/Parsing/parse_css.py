from WebBrowser.Tokens import Tokens, CSSTokens
from WebBrowser.Tokens.CSSTokens import CSS_map
import io


class CSSParser(object):

    def __init__(self):


if __name__ == '__main__':
    with io.open("C:/Users/Dan/Desktop/Programming/Github/WebBrowser/WebBrowser/test_pages/small.css", 'r') as f:
        css = f.read()
        print css
        print CSSParser(css)