from units import SchemaUnit

from unit_types import Mapping, ObjectMapping, Sequence


__all__ = ['MappingSchema', 'ObjectMappingSchema', 'SequenceSchema']


# Mapping schema

class MappingSyncMixin(object):
    def sync(self, instance=None, value=None):
        if instance is None:
            instance = self.instance

        if value is None:
            value = self.validated_data

        assert instance is not None, "Cannot sync with None value."

        value = self.prepare_to_sync(instance, value)
        for name, subval in value.iteritems():
            self.children[name].sync(instance, subval)


class MappingSchema(MappingSyncMixin, SchemaUnit):
    schema_type = Mapping


class ObjectMappingSchema(MappingSyncMixin, SchemaUnit):
    schema_type = ObjectMapping


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

        if value is None:
            value = self.validated_data

        assert instance is not None, "Cannot sync with None value."

        if isinstance(instance, list):
            del instance[:]
            instance_seq = instance
        else:
            instance_seq = getattr(instance, self.name, None)
            if instance_seq is None:
                instance_seq = []
                setattr(instance, self.name, instance_seq)
            else:
                del instance_seq[:]

        value = self.prepare_to_sync(instance, value)
        child = self.children.values()[0]
        for i in xrange(len(value)):
            child.sync(instance_seq, value[i])
