from Tokens.Tokens import Token

CSS_map = {':': 'ASSIGN', ';': 'ENDASSIGN', '{': 'LBRACK',
           '}': 'RBRACK', '#': 'ID', '.': 'CLASS'}


class CSSToken(Token):

    def __init__(self, char):
        super(CSSToken, self).__init__(char)

    @property
