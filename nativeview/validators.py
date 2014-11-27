from exceptions import ValidationError


class MinMaxInterface(object):
    min = None
    max = None


class ChoicesInterface(object):
    choices = None


class Choices(ChoicesInterface):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, unit, value):
        if not value in self.choices:
            choices = ', '.join(['%s' % c for c in self.choices])
            msg = "%s is not one of %s" % (value, choices)
            raise ValidationError(msg, unit)
