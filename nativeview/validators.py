import re

from exceptions import ValidationError
from i18n import TranslationStringFactory as _


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

    def get_metadata(self, unit):
        metadata = {}
        for validator in self.validators:
            if hasattr(validator, 'get_metadata'):
                metadata.update(validator.get_metadata(unit))
        return metadata


class Choices(object):
    error_message = _("'${value}' is not one of ${choices_values}.")

    def __init__(self, iter_or_func):
        """
        :iter_or_func: any iterable or callable object.
        """
        if not callable(iter_or_func):
            self.get_choices = lambda: iter_or_func
        else:
            self.get_choices = iter_or_func

    def __iter__(self):
        """Returns tuple of value and label on each iteration."""
        for item in self.get_choices():
            if isinstance(item, (list, tuple)) and len(item) == 2:
                yield item[0], item[1]
            else:
                yield item, item

    def __call__(self, unit, value):
        choices_values = [v for v, l in self]
        if value not in choices_values:
            choices_values = ', '.join('%s' % v for v in choices_values)
            detail = self.error_message % {
                'value': value, 'choices_values': choices_values}
            raise ValidationError(detail, unit)

    def get_metadata(self, unit):
        return {'choices': [dict(value=v, label=l) for v,l in self]}


class Range(object):
    min_error_message = _("'${value}' is less than minimum value ${min}.")
    max_error_message = _("'${value}' is greater than maximum value ${max}.")

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, unit, value):
        if self.min is not None:
            if value < self.min:
                detail = self.min_error_message % \
                    {'value': value, 'min': self.min}
                raise ValidationError(detail, unit)

        if self.max is not None:
            if value > self.max:
                detail = self.max_error_message % \
                    {'value': value, 'max': self.max}
                raise ValidationError(detail, unit)

    def get_metadata(self, unit):
        metadata = {}

        if self.min is not None:
            metadata['min'] = self.min

        if self.max is not None:
            metadata['max'] = self.max

        return metadata


class Length(object):
    min_error_message = _('Shorter than minimum length ${min}.')
    max_error_message = _('Longer than maximum length ${max}.')

    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, unit, value):
        if self.min is not None:
            if len(value) < self.min:
                detail = self.min_error_message % {'min': self.min}
                raise ValidationError(detail, unit)

        if self.max is not None:
            if len(value) > self.max:
                detail = self.max_error_message % {'max': self.max}
                raise ValidationError(detail, unit)

    def get_metadata(self, unit):
        metadata = {}

        if self.min is not None:
            metadata['min'] = self.min

        if self.max is not None:
            metadata['max'] = self.max

        return metadata


class Regex(object):
    error_message = _("String does not match expected pattern.")

    def __init__(self, regex, error_message=None):
        self.match_object = re.compile(regex)
        if error_message is not None:
            self.error_message = error_message

    def __call__(self, unit, value):
        if self.match_object.match(value) is None:
            raise ValidationError(self.error_message, unit)


class Email(Regex):
    regex = "(?i)^[A-Z0-9._%!#$%&'*+-/=?^_`{|}~()]+@[A-Z0-9]+([.-][A-Z0-9]+)*\.[A-Z]{2,8}$"
    error_message = _("Invalid email address.")

    def __init__(self, error_message=None):
        if error_message is not None:
            self.error_message = error_message
        super(Email, self).__init__(self.regex)
