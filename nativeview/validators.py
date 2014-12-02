import re

from exceptions import ValidationError


class ValidatedChain(object):
    def __init__(self, *validators):
        self.validators = validators

    def __call__(self, unit, value):
        errors = []
        for validator in self.validators:
            try:
                validator(unit, value)
            except ValidationError as e:
                errors.extend(e.detail)

        if errors:
            exc = ValidationError(errors, unit)
            raise exc

    def get_metadata(self):
        metadata = {}
        for validator in self.validators:
            if hasattr(validator, 'get_metadata'):
                metadata.update(validator.get_metadata())
        return metadata


class Choices(object):
    error_message = "%s is not one of %s."
    def __init__(self, choices):
        """
        :choices: object with iterator interface.
        """
        self.choices = choices

    def __call__(self, unit, value):
        if not value in self.choices:
            choices = ', '.join('%s' % c for c in self.choices)
            self.error_message % (value, choices)
            raise ValidationError(msg, unit)

    def get_metadata(self):
        return {'choices': list(self.choices)}


class Range(object):
    min_error_message = '%s is less than minimum value %s.'
    max_error_message = '%s is greater than maximum value %s.'

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, unit, value):
        if self.min is not None:
            if value < self.min:
                raise ValidationError(
                    self.min_error_message % (value, self.min), unit)

        if self.max is not None:
            if value > self.max:
                raise ValidationError(
                    self.max_error_message % (value, self.max), unit)

    def get_metadata(self):
        metadata = {}

        if self.min is not None:
            metadata['min'] = self.min

        if self.max is not None:
            metadata['max'] = self.max

        return metadata


class Length(object):
    min_error_message = 'Shorter than minimum length %s.'
    max_error_message = 'Longer than maximum length %s.'

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, unit, value):
        if self.min is not None:
            if len(value) < self.min:
                raise ValidationError(self.min_error_message % self.min, unit)

        if self.max is not None:
            if len(value) > self.max:
                raise ValidationError(self.max_error_message % self.max, unit)

    def get_metadata(self):
        metadata = {}

        if self.min is not None:
            metadata['min'] = self.min

        if self.max is not None:
            metadata['max'] = self.max

        return metadata


class Regex(object):
    error_message = "String does not match expected pattern."
    def __init__(self, regex, error_message=None):
        self.match_object = re.compile(regex)
        if error_message is not None:
            self.error_message = error_message

    def __call__(self, unit, value):
        if self.match_object.match(value) is None:
            raise ValidationError(self.error_message, unit)


class Email(Regex):
    regex = "(?i)^[A-Z0-9._%!#$%&'*+-/=?^_`{|}~()]+@[A-Z0-9]+([.-][A-Z0-9]+)*\.[A-Z]{2,8}$"
    error_message = "Invalid email address."
    def __init__(self, error_message=None):
        if error_message is not None:
            self.error_message = error_message
        super(Email, self).__init__(self.regex)
