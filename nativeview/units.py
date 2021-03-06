import copy
import itertools
from collections import OrderedDict

from exceptions import ValidationError
from i18n import TranslationStringFactory as _


__all__ = ['SchemaUnit']


class empty:
    pass


class SkipUnit(Exception):
    pass


# Schema units

class _SchemaUnit(object):
    _counter = itertools.count()

    default_error_messages = {
        'required': _('This field is required.'),
        'none': _('None does not allow.')
    }

    def __new__(cls, *args, **kw):
        unit = object.__new__(cls)
        unit.children = OrderedDict()
        for name, child in cls.__schema_units__.iteritems():
            unit.children[name] = copy.deepcopy(child)
        unit._order = next(cls._counter)
        for child in unit.children.itervalues():
            child.parent = unit
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
        self.parent = None

        self.validator = kwargs.pop('validator', None)
        self._initial_data = kwargs.pop('data', empty)

        self.source_object = kwargs.pop('object', None)

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(kwargs.pop('error_messages', {}))
        self.error_messages = messages

        self.required = kwargs.pop('required', True)
        self.default = kwargs.pop('default', empty)
        self.read_only = kwargs.pop('read_only', False)
        self.allow_none = kwargs.pop('allow_none', False)
        self._context = kwargs.pop('context', {})

        # Omit if object has __len__ method and this method returns zero
        # Only for serialization.
        self.omit_if_empty = kwargs.pop('omit_if_empty', False)
        self.omit_if_none = kwargs.pop('omit_if_none', False)

        self.preparer = kwargs.pop('preparer', None)

        assert not kwargs, 'Unknown arguments: %s' % kwargs

    @property
    def schema_type(self):
        raise NotImplementedError

    def bind(self, object=empty, context=empty, data=empty):
        if object is not empty:
            self.source_object = object
        if context is not empty:
            self._context = context
        if data is not empty:
            self._initial_data = data

    def reset(self):
        self.source_object = None
        self._context = {}
        self._initial_data = empty

    def serialize(self, value=empty):
        if value is empty:
            value = self.source_object
        return self.type.serialize(value)

    def deserialize(self, value=empty):
        return self.type.deserialize(value)

    def get_default(self):
        if self.default is empty:
            raise SkipUnit
        return self.default

    def run_validation(self, data=empty):
        if self.preparer is not None:
            data = self.preparer(data)

        if self.read_only:
            return self.get_default()

        if data is empty:
            if self.required:
                raise ValidationError(self.error_messages['required'])
            return self.get_default()

        if data is None:
            if not self.allow_none:
                raise ValidationError(self.error_messages['none'])
            return None

        value = self.deserialize(data)
        if self.validator:
            self.validator(self, value)
        return value

    def is_valid(self):
        self._errors = False
        try:
            self._validated_data = self.run_validation(self._initial_data)
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
    def validated_data(self):
        assert hasattr(self, '_validated_data'), \
            'You must call `.is_valid()` before accessing `.validated_data`.'
        if self._validated_data is empty:
            return None
        return self._validated_data

    @property
    def root(self):
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    @property
    def context(self):
        return getattr(self.root, '_context', {})


class SchemaMeta(type):
    def __new__(meta, class_name, bases, new_attrs):
        units = []
        for name, value in new_attrs.items():
            if isinstance(value, _SchemaUnit):
                del new_attrs[name]
                if value.name is None:
                    value.name = name
                units.append((name, value))

        units.sort(key=lambda el: el[1]._order)

        # Inherit super classes children.
        for base in reversed(bases):
            if hasattr(base, '__schema_units__'):
                units = list(base.__schema_units__.iteritems()) + units

        new_attrs['__schema_units__'] = OrderedDict(units)

        return type.__new__(meta, class_name, bases, new_attrs)


class SchemaUnit(_SchemaUnit):
    __metaclass__ = SchemaMeta
