import abc


class TokenStream(object):
    _raw = []
    _index = 0

    def __init__(self, string):
        self.raw = string

    @property
    def raw(self):
        return self._raw

    @raw.setter
    def raw(self, string):
        self._raw.extend(string)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, new_index):
        if new_index >= len(self.raw):
            self._index = new_index % len(self.raw)
        else:
            self._index = new_index

    def get_next(self):
        self.index += 1
        return self.raw[self.index-1]

    def peek(self, num):
        try:
            return self.raw[self.index + num]
        except IndexError:
            return self.raw[(self.index + num) % len(self.raw)]


class Token(str):
    __metaclass__ = abc.ABCMeta

    _key = ''
    _value = ""

    def __init__(self, char):
        self.key = char

    @abc.abstractproperty
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @key.setter
    def key(self, char):
        raise NotImplementedError
