from units import SchemaUnit

from unit_types import Mapping, ObjectMapping, Sequence
from units import empty


__all__ = [
    'SyncedSchemaUnit', 'MappingSchema', 'ObjectMappingSchema',
    'SequenceSchema'
]


# Mapping schema

class SyncedSchemaUnit(SchemaUnit):
    def sync(self, instance=None, value=empty):
        """
        Bind value data to instance, also may create a new instance
        if passed instance is None.

        Args:
            instance - Existing instance, all data will be bind to the instance.
            value - A validated data to bind to the instance.
        """
        raise NotImplementedError


class MappingSchema(SyncedSchemaUnit):
    schema_type = Mapping

    def sync(self, instance=None, value=empty):
        # Everytime create a new dict
        instance = {}

        if value is empty:
            value = self.validated_data

        assert value is not empty, 'Cannot process empty value'

        for name, subval in value.iteritems():
            child = self.children[name]
            if subval is not empty and isinstance(child, SyncedSchemaUnit):
                subinstance = instance.get(child.name)
                subval = child.sync(instance=subinstance, value=subval)
            instance[child.name] = subval

        return instance


class ObjectMappingSchema(SyncedSchemaUnit):
    schema_type = ObjectMapping

    def sync(self, instance=None, value=empty):
        if instance is None:
            instance = self.source_object

        if value is empty:
            value = self.validated_data

        assert instance is not None, 'Cannot sync with None value'
        assert value is not empty, 'Cannot process empty value'

        for name, subval in value.iteritems():
            child = self.children[name]
            if subval is not empty and isinstance(child, SyncedSchemaUnit):
                subinstance = getattr(instance, child.name, None)
                subval = child.sync(instance=subinstance, value=subval)
            setattr(instance, child.name, subval)

        return instance


class SequenceSchema(SyncedSchemaUnit):
    schema_type = Sequence

    def __init__(self, *args, **kw):
        super(SequenceSchema, self).__init__(*args, **kw)
        if len(self.children) != 1:
            raise TypeError(
                'Sequence schemas must have exactly one child unit')

    def sync(self, instance=None, value=empty):
        # Everytime create a new list
        instance = []

        if value is empty:
            value = self.validated_data

        assert value is not empty, 'Cannot process empty value'

        child = self.children.values()[0]
        for subval in value:
            if subval is not empty and isinstance(child, SyncedSchemaUnit):
                subval = child.sync(value=subval)
            instance.append(subval)

        return instance
