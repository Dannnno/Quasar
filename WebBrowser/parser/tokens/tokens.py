import abc


class Token(str):
    __metaclass__ = abc.ABCMeta
    _key = ''
    _value = ''

    @abc.abstractproperty
    def key(self):
        return self._key

    @abc.abstractproperty
    def value(self):
        return self._value
