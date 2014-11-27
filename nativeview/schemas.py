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

        for name, value in self.validated_data.iteritems():
            self.children[name].sync(instance, value)


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
            instance.extend(value)
        else:
            instance_seq = getattr(instance, self.name, None)
            if instance_seq is None:
                setattr(instance, self.name, instance)
            else:
                del instance_seq[:]
                instance_seq.extend(value)
