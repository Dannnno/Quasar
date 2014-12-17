import abc


class Token(abc.ABCMeta):
    _regex = ''
    _value = ''

    @abc.abstractproperty
    def regex(self):
        raise NotImplementedError

    @abc.abstractproperty
    def value(self):
        raise NotImplementedError
