from units import SchemaUnit

from unit_types import Mapping, ObjectMapping, Sequence


__all__ = ['MappingSchema', 'ObjectMappingSchema', 'SequenceSchema']


# Mapping schema

class SchemaBase(object):
    def restore_object(self, validated_data):
        raise NotImplementedError

    def sync(self, instance=None, value=None):
        raise NotImplementedError

    def sync_impl(self, instance, value, callback):
        if value is None:
            value = self.validated_data

        if instance is None:
            instance = self.instance

        if instance is None:
            instance = self.restore_object(value)

        callback(instance, value)

        return instance


class MappingSchema(SchemaBase, SchemaUnit):
    schema_type = Mapping

    def restore_object(self, validated_data):
        return {}

    def sync(self, instance=None, value=None):
        def callback(instance, value):
            for name, subval in value.iteritems():
                child = self.children[name]
                if hasattr(child, 'sync'):
                    subval = child.sync(value=subval)
                instance[name] = subval

        return self.sync_impl(instance, value, callback)


class ObjectMappingSchema(SchemaBase, SchemaUnit):
    schema_type = ObjectMapping

    def sync(self, instance=None, value=None):
        def callback(instance, value):
            for name, subval in value.iteritems():
                child = self.children[name]
                if hasattr(child, 'sync'):
                    subval = child.sync(value=subval)
                setattr(instance, name, subval)

        return self.sync_impl(instance, value, callback)


class SequenceSchema(SchemaBase, SchemaUnit):
    schema_type = Sequence

    def __init__(self, *args, **kw):
        super(SequenceSchema, self).__init__(*args, **kw)
        if len(self.children) != 1:
            raise TypeError(
                'Sequence schemas must have exactly one child unit')

    def restore_object(self, validated_data):
        return []

    def sync(self, instance=None, value=None):
        def callback(instance, value):
            child = self.children.values()[0]
            for i in xrange(len(value)):
                subval = value[i]
                if hasattr(child, 'sync'):
                    subval = child.sync(value=subval)
                instance.append(subval)

        return self.sync_impl(instance, value, callback)
