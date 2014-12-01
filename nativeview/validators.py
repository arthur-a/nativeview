from exceptions import ValidationError


class Choices(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, unit, value):
        if not value in self.choices:
            choices = ', '.join(['%s' % c for c in self.choices])
            msg = "%s is not one of %s" % (value, choices)
            raise ValidationError(msg, unit)

    def get_metadata(self):
        return {'choices': self.choices}


class Range(object):
    min_error_message = '%s is less than minimum value %s'
    max_error_message = '%s is greater than maximum value %s'

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, node, value):
        if self.min is not None:
            if value < self.min:
                raise Invalid(node, self.min_error_message % (value, self.min))

        if self.max is not None:
            if value > self.max:
                raise Invalid(node, self.max_error_message % (value, self.max))

    def get_metadata(self):
        metadata = {}

        if self.min is not None:
            metadata['min'] = self.min

        if self.max is not None:
            metadata['max'] = self.max

        return metadata


class Length(object):
    min_error_message = 'Shorter than minimum length %s'
    max_error_message = 'Longer than maximum length %s'

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, node, value):
        if self.min is not None:
            if len(value) < self.min:
                raise Invalid(node, self.min_error_message % self.min)

        if self.max is not None:
            if len(value) > self.max:
                raise Invalid(node, self.max_error_message % self.max)

    def get_metadata(self):
        metadata = {}

        if self.min is not None:
            metadata['min'] = self.min

        if self.max is not None:
            metadata['max'] = self.max

        return metadata
