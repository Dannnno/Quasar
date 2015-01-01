class ParseError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


class CSSSyntaxError(ParseError):

    def __init__(self, message):
        super(CSSSyntaxError, self).__init__(message)
