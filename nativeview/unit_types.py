from collections import OrderedDict
import datetime

import arrow


__all__ = [
    'ValidationError', 'Integer', 'DateTime', 'Date',
    'String', 'Mapping', 'ObjectMapping', 'Sequence'
]



class ValidationError(Exception):
    def __init__(self, msg, unit):
        super(ValidationError, self).__init__(msg)


# UnitTypes

class UnitType(object):
    omit_if_none = False

    # Omit if object has __len__ method and this method returns zero
    omit_if_empty = False

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
        'invalid': 'Enter a whole number.'
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


ISO_8601 = 'iso-8601'
class DateTime(UnitType):
    default_error_messages = {
        'invalid': "Datetime has wrong format. Use this format instead: %s",
    }
    format = 'YYYY-MM-DDTHH:mm:ssZZ'

    def __init__(self, format=None, *args, **kwargs):
        self.format = format if format is not None else self.format
        super(DateTime, self).__init__(*args, **kwargs)

    def serialize(self, value):
        if value is None:
            return value

        return arrow.get(value).format(self.format)

    def deserialize(self, value):
        if self.format.lower() == ISO_8601:
            try:
                return isodate.parse_date(value)
            except (TypeError, ValueError):
                parsed = datetime.datetime.strptime(value, format)
        else:
            return isodate.parse_date(value)

        msg = self.error_messages['invalid'] % self.format
        raise ValidationError(msg, self.unit)


class Date(UnitType):
    default_error_messages = {
        'invalid': "Date has wrong format. Use this format instead: %s",
    }
    format = 'YYYY-MM-DD'

    def __init__(self, format=None, *args, **kwargs):
        self.format = format if format is not None else self.format
        super(Date, self).__init__(*args, **kwargs)

    def serialize(self, value):
        if value is None:
            return value

        return arrow.get(value).format(self.format)


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


class Mapping(UnitType):
    def serialize(self, value):
        if value is None:
            return None

        result = OrderedDict()
        for name, unit in self.unit.children.iteritems():
            subvalue = value.get(name)
            serialized = unit.serialize(subvalue)
            if serialized is None and unit.type.omit_if_none:
                continue
            if (unit.type.omit_if_empty and
                    hasattr(serialized, '__len__') and
                    len(serialized) == 0):
                continue
            result[name] = serialized
        return result

    def deserialize(self, data):
        result = {}
        for name, unit in self.unit.children.iteritems():
            value = data.get(name)
            deserialized = unit.deserialize(value)
            result[name] = deserialized
        return result


class ObjectMapping(UnitType):
    def serialize(self, value):
        if value is None:
            return None

        result = OrderedDict()
        for name, unit in self.unit.children.iteritems():
            subvalue = getattr(value, name, None)
            serialized = unit.serialize(subvalue)
            if serialized is None and unit.type.omit_if_none:
                continue
            if (unit.type.omit_if_empty and
                    hasattr(serialized, '__len__') and
                    len(serialized) == 0):
                continue
            result[name] = serialized
        return result


class Sequence(UnitType):
    def serialize(self, value):
        if value is None:
            return None

        result = []
        child = self.unit.children.values()[0]
        for subval in value:
            serialized = child.serialize(subval)
            if serialized is None and child.type.omit_if_none:
                continue
            if (child.type.omit_if_empty and
                    hasattr(serialized, '__len__') and
                    len(serialized) == 0):
                continue
            result.append(serialized)
        return result
