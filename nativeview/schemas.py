from units import SchemaUnit

from unit_types import Mapping, ObjectMapping, Sequence


__all__ = ['MappingSchema', 'ObjectMappingSchema', 'SequenceSchema']


# Mapping schema

class MappingSchema(SchemaUnit):
    schema_type = Mapping

    def sync(self, instance=None, value=None):
        if instance is None:
            instance = self.instance

        if value is None:
            value = self.validated_data

        assert instance is not None, "Cannot sync with None value."

        for name, value in self.validated_data.iteritems():
            self.children[name].sync(instance, value)


class ObjectMappingSchema(SchemaUnit):
    schema_type = ObjectMapping


class SequenceSchema(SchemaUnit):
    schema_type = Sequence

    def __init__(self, *args, **kw):
        super(SequenceSchema, self).__init__(*args, **kw)
        if len(self.children) != 1:
            raise TypeError(
                'Sequence schemas must have exactly one child unit')
