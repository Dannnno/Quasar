__all__ = ['css_ast']


from copy import deepcopy


class ASTNode(object):

    def __init__(self, token, parent, children):
        self.token = token
        self.parent = parent
        self.children = deepcopy(children)

