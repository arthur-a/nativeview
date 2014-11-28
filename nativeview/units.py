import itertools
from collections import OrderedDict

from exceptions import ValidationError


__all__ = ['SchemaUnit']


class empty: pass


# Schema units

class _SchemaUnit(object):
    _counter = itertools.count()
    schema_type = None

    def __new__(cls, *args, **kw):
        unit = object.__new__(cls)
        unit.children = OrderedDict(cls.__schema_units__)
        unit._order = next(cls._counter)
        return unit

    def __init__(self, *args, **kwargs):
        name = type_ = None
        args = list(args)
        if args:
            if isinstance(args[0], basestring):
                name = args.pop(0)

        if args:
            type_ = args[0]
        else:
            type_ = self.schema_type()

        type_.unit = self
        self.type = type_
        self.name = name
        self.validator = kwargs.get('validator')
        self.serialized_data = kwargs.get('serialized_data', empty)
        self.deserialized_data = kwargs.get('deserialized_data', empty)
        self.required = kwargs.get('required', False)
        self.read_only = kwargs.get('read_only', False)
        self.instance = kwargs.get('instance')

    def serialize(self, value=empty):
        if value is empty:
            value = self.deserialized_data
        return self.type.serialize(value)

    def deserialize(self, value=empty):
        if value is empty:
            value = self.serialized_data
        return self.type.deserialize(value)

    def run_validation(self, value=empty):
        data = self.deserialize(value)
        if self.validator:
            self.validator(self, data)
        return data

    def is_valid(self, value=empty):
        self._errors = False
        try:
            self._validated_data = self.run_validation(value)
        except ValidationError as e:
            self._validated_data = empty
            self._errors = e.detail

        return not bool(self._errors)

    @property
    def errors(self):
        assert hasattr(self, '_errors'), \
            'You must call `.is_valid()` before accessing `.errors`.'
        return self._errors

    @property
    def errors(self):
        assert hasattr(self, '_errors'), \
            'You must call `.is_valid()` before accessing `.errors`.'
        return self._errors

    @property
    def validated_data(self):
        assert hasattr(self, '_validated_data'), \
            'You must call `.is_valid()` before accessing `.validated_data`.'
        if self._validated_data is empty:
            return None
        return self._validated_data


class SchemaMeta(type):
    def __new__(meta, class_name, bases, new_attrs):
        units = []
        for name, value in new_attrs.items():
            if isinstance(value, _SchemaUnit):
                del new_attrs[name]
                value.name = name
                units.append((value._order, name, value))

        cls = type.__new__(meta, class_name, bases, new_attrs)

        units.sort()
        cls.__schema_units__ = OrderedDict(u[1:] for u in units)

        return cls


class SchemaUnit(_SchemaUnit):
    __metaclass__ = SchemaMeta
