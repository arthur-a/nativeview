from units import SchemaUnit

from unit_types import Mapping, ObjectMapping, Sequence


__all__ = ['MappingSchema', 'ObjectMappingSchema', 'SequenceSchema']


# Mapping schema

def mapping_sync(unit, value, setter):
    for name, subval in value.iteritems():
        child = unit.children[name]
        if hasattr(child, 'sync'):
            subval = child.sync(value=subval)
        setter(name, subval)


class MappingSchema(SchemaUnit):
    schema_type = Mapping

    def sync(self, instance=None, value=None):
        if instance is None:
            instance = self.instance

        if instance is None:
            instance = {}

        if value is None:
            value = self.validated_data


        setter = lambda n, v: instance.__setitem__(n, v)
        mapping_sync(self, value, setter)
        return instance


class ObjectMappingSchema(SchemaUnit):
    schema_type = ObjectMapping

    def restore_object(self, validated_data):
        raise NotImplementedError

    def sync(self, instance=None, value=None):
        if value is None:
            value = self.validated_data

        if instance is None:
            instance = self.instance

        if instance is None:
            instance = self.restore_object(value)

        setter = lambda n, v: setattr(instance, n, v)
        mapping_sync(self, value, setter)
        return instance


class SequenceSchema(SchemaUnit):
    schema_type = Sequence

    def __init__(self, *args, **kw):
        super(SequenceSchema, self).__init__(*args, **kw)
        if len(self.children) != 1:
            raise TypeError(
                'Sequence schemas must have exactly one child unit')

    def sync(self, instance=None, value=None):
        if instance is None:
            instance = self.instance

        if instance is None:
            instance = []

        if value is None:
            value = self.validated_data

        child = self.children.values()[0]
        for i in xrange(len(value)):
            subval = value[i]
            if hasattr(child, 'sync'):
                subval = child.sync(value=subval)
            instance.append(subval)

        return instance
