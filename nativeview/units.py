import itertools
from collections import OrderedDict


__all__ = ['SchemaUnit']


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
        self.serialized_data = kwargs.get('serialized_data')
        self.deserialized_data = kwargs.get('deserialized_data')
        self.required = kwargs.get('required', False)
        self.read_only = kwargs.get('read_only', False)

    def serialize(self, value=None):
        if value is None:
            value = self.deserialized_data
        return self.type.serialize(value)

    def deserialize(self):
        raise NotImplementedError

    def is_valid(self):
        raise NotImplementedError


class SchemaMeta(type):
    def __new__(meta, class_name, bases, new_attrs):
        units = []
        for name, value in new_attrs.items():
            if isinstance(value, _SchemaUnit):
                del new_attrs[name]
                units.append((value._order, name, value))

        cls = type.__new__(meta, class_name, bases, new_attrs)

        units.sort()
        cls.__schema_units__ = OrderedDict(u[1:] for u in units)

        return cls


class SchemaUnit(_SchemaUnit):
    __metaclass__ = SchemaMeta
