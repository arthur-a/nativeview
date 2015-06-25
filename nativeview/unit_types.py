from collections import OrderedDict
import datetime
import translationstring

import arrow

from exceptions import ValidationError
from units import empty, SkipUnit
from i18n import TranslationStringFactory as _


__all__ = [
    'ValidationError', 'Integer', 'Float',
    'DateTime', 'Date', 'String',
    'FileFieldStorage', 'Boolean', 'Mapping',
    'ObjectMapping', 'Sequence'
]


# UnitTypes

class UnitType(object):
    def __init__(
            self, unit=None,
            error_messages=None,
            **kwargs
        ):
        self.unit = unit

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

        self.__dict__.update(kwargs)

    def serialize(self, value):
        raise NotImplementedError

    def deserialize(self, value):
        raise NotImplementedError


class Integer(UnitType):
    default_error_messages = {
        'invalid': _('Enter a whole number.')
    }

    def serialize(self, value):
        if value is None:
            return value

        if isinstance(value, int):
            return value

        return int(str(value))

    def deserialize(self, value):
        try:
            return int(str(value))
        except (TypeError, ValueError):
            raise ValidationError(self.error_messages['invalid'], self.unit)


class Float(UnitType):
    default_error_messages = {
        'invalid': _('Enter a floating-point number.')
    }

    def serialize(self, value):
        if value is None:
            return value

        if isinstance(value, float):
            return value

        return float(str(value))

    def deserialize(self, value):
        try:
            return float(str(value))
        except (TypeError, ValueError):
            raise ValidationError(self.error_messages['invalid'], self.unit)


class DateTime(UnitType):
    default_error_messages = {
        'invalid': _(
            "Datetime has wrong format. Use this format instead: '${format}'."),
    }
    format = 'YYYY-MM-DDTHH:mm:ss.SSSZZ'
    input_formats = [
        'YYYY-MM-DDTHH:mm:ssZZ',
        'YYYY-MM-DDTHH:mm:ss.SSSZZ',
        'YYYY-MM-DDTHH:mm:ss.SSS'
    ]

    def __init__(self, format=None, *args, **kwargs):
        self.format = format if format is not None else self.format
        super(DateTime, self).__init__(*args, **kwargs)

    def serialize(self, value):
        if value is None:
            return value

        try:
            return arrow.get(value).format(self.format)
        except arrow.parser.ParserError as e:
            raise ValueError(e.message)

    def deserialize(self, value):
        try:
            return arrow.get(value, self.input_formats).datetime
        except (TypeError, arrow.parser.ParserError):
            msg = self.error_messages['invalid'] % {'format': self.format}
            raise ValidationError(msg, self.unit)


class Date(UnitType):
    default_error_messages = {
        'invalid': _(
            "Date has wrong format. Use this format instead: '${format}'."),
    }
    format = 'YYYY-MM-DD'

    def __init__(self, format=None, *args, **kwargs):
        self.format = format if format is not None else self.format
        super(Date, self).__init__(*args, **kwargs)

    def serialize(self, value):
        if value is None:
            return value

        try:
            return arrow.get(value).format(self.format)
        except arrow.parser.ParserError as e:
            raise ValueError(e.message)

    def deserialize(self, value):
        try:
            return arrow.get(value, self.format).date()
        except (TypeError, arrow.parser.ParserError):
            msg = self.error_messages['invalid'] % {'format': self.format}
            raise ValidationError(msg, self.unit)


class String(UnitType):
    def serialize(self, value):
        if value is None:
            return value

        if isinstance(value, basestring):
            return value

        return unicode(value)

    def deserialize(self, value):
        if isinstance(value, basestring):
            return value

        if value is None:
            return None

        return unicode(value)


class FileFieldStorage(UnitType):
    default_error_messages = {
        'invalid': _("The submitted data was not a file."),
    }

    def serialize(self, value):
        if value is None:
            return value

        return value.filename

    def deserialize(self, data):
        if data is None:
            return None

        try:
            file_name = data.filename
            file_size = data.file
        except AttributeError:
            message = self.error_messages['invalid']
            raise ValidationError(message, self.unit)

        return data


class Boolean(UnitType):
    default_error_messages = {
        'invalid': _('Invalid boolean value.')
    }
    TRUE_VALUES = set(('t', 'T', 'true', 'True', 'TRUE', '1', 1, True))
    FALSE_VALUES = set(('f', 'F', 'false', 'False', 'FALSE', '0', 0, 0.0, False))

    def serialize(self, value):
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        return bool(value)

    def deserialize(self, data):
        if data in self.TRUE_VALUES:
            return True
        elif data in self.FALSE_VALUES:
            return False
        raise ValidationError(self.default_error_messages['invalid'], self.unit)


def allow_to_serialize(unit, serialized):
    if serialized is None and unit.omit_if_none:
        return False
    if (unit.omit_if_empty and
            hasattr(serialized, '__len__') and
            len(serialized) == 0):
        return False

    return True


class MappingDeserializeMixin(object):
    def deserialize(self, data):
        # TODO: To check data for dictionary
        result = OrderedDict()
        errors = OrderedDict()

        for name, unit in self.unit.children.iteritems():
            # TODO: raise an error or not?
            if unit.read_only:
                continue
            value = data.get(name, empty)
            try:
                validated_value = unit.run_validation(value)
            except ValidationError as e:
                errors[name] = e.detail
            except SkipUnit:
                pass
            else:
                result[name] = validated_value

        if errors:
            raise ValidationError(errors)

        return result


class Mapping(MappingDeserializeMixin, UnitType):
    def serialize(self, value):
        if value is None:
            return None

        result = OrderedDict()
        for name, unit in self.unit.children.iteritems():
            key = unit.name or name
            subvalue = value.get(key)
            serialized = unit.serialize(subvalue)
            if not allow_to_serialize(unit, serialized):
                continue
            result[name] = serialized
        return result


class ObjectMapping(MappingDeserializeMixin, UnitType):
    def serialize(self, value):
        if value is None:
            return None

        result = OrderedDict()
        for name, unit in self.unit.children.iteritems():
            attrname = unit.name or name
            subvalue = getattr(value, attrname, None)
            serialized = unit.serialize(subvalue)
            if not allow_to_serialize(unit, serialized):
                continue
            result[name] = serialized
        return result


class Sequence(UnitType):
    default_error_messages = {
        'iterable': _("'${value}' is not a sequence."),
    }

    def _validate_seq(self, value):
        if isinstance(value, list):
            return value
        elif (hasattr(value, '__iter__') and
            not hasattr(value, 'get') and
            not isinstance(value, basestring)):
            return list(value)
        else:
            detail = self.error_messages['iterable'] % {'value': value}
            raise ValidationError(detail, self.unit)

    def serialize(self, value):
        if value is None:
            return None

        result = []
        child = self.unit.children.values()[0]
        for subval in value:
            serialized = child.serialize(subval)
            if not allow_to_serialize(child, serialized):
                continue
            result.append(serialized)
        return result

    def deserialize(self, value):
        value = self._validate_seq(value)
        result = []
        errors = OrderedDict()

        child = self.unit.children.values()[0]
        if self.unit.read_only:
            # TODO: Do it in run_validation method in unit instance.
            if self.unit.name:
                detail = "%s is read only value." % self.unit.name
            else:
                detail = "Read only value."
            raise ValidationError(detail, self.unit)

        for num, subval in enumerate(value):
            try:
                validated_value = child.run_validation(subval)
            except ValidationError as e:
                errors[num] = e.detail
            except SkipUnit:
                pass
            else:
                result.append(validated_value)

        if errors:
            raise ValidationError(errors)

        return result
