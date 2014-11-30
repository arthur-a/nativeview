import unittest

from nativeview import (
    ValidationError,
    Integer, DateTime, Date, String, SchemaUnit,
    SequenceSchema, ObjectMappingSchema, MappingSchema)
from nativeview.metadata import determine_metadata


class TestMappingObject(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class StrSeqUnit(SequenceSchema):
    item = SchemaUnit(String())


class IntSeqUnit(SequenceSchema):
    item = SchemaUnit(Integer())


class TestMappingSchema(MappingSchema):
    int_unit = SchemaUnit(Integer())
    str_unit = SchemaUnit(String())
    str_seq_unit = StrSeqUnit()
    int_seq_unit = IntSeqUnit()


class TestObjectSchema(ObjectMappingSchema):
    int_unit = SchemaUnit(Integer())
    str_unit = SchemaUnit(String())
    str_seq_unit = StrSeqUnit()
    int_seq_unit = IntSeqUnit()

    def restore_object(self, validated_data):
        return TestMappingObject(**validated_data)


class TestMappingSchemaNested1(MappingSchema):
    int_unit = SchemaUnit(Integer())
    nested_dict_schema = TestMappingSchema()


class TestObjectSchemaNested1(ObjectMappingSchema):
    int_unit = SchemaUnit(Integer())
    nested_obj_schema = TestObjectSchema()


class TestMappingSchemaCase(unittest.TestCase):
    def setUp(self):
        self.source_object = {
            'int_unit': 123,
            'str_unit': 'Some string',
            'str_seq_unit': ['string1', 'string2'],
            'int_seq_unit': [1,2,3,4]
        }
        self.deserialized_data = self.source_object
        self.serialized_data = {
            'int_unit': 123,
            'str_unit': 'Some string',
            'str_seq_unit': ['string1', 'string2'],
            'int_seq_unit': [1, 2, 3, 4]
        }
        self.object_to_sync = {}
        self.expected_synced_object = self.source_object

    def test_serialize_ok(self):
        schema = TestMappingSchema(object=self.source_object)
        self.assertDictEqual(
            dict(schema.serialize()), self.serialized_data)

    def test_deserialize_ok(self):
        schema = TestMappingSchema(data=self.serialized_data)
        self.assertDictEqual(
            dict(schema.deserialize()), self.deserialized_data)

    def test_sync(self):
        schema = TestMappingSchema(
            object=self.object_to_sync,
            data=self.serialized_data)
        self.assertTrue(schema.is_valid())
        schema.sync()
        self.assertDictEqual(
            self.object_to_sync, self.expected_synced_object)


class TestNested1MappingSchemaCase(unittest.TestCase):
    def setUp(self):
        self.source_object = {
            'int_unit': 123,
            'nested_dict_schema': {
                'int_unit': 123,
                'str_unit': 'Some string',
                'str_seq_unit': ['string1', 'string2'],
                'int_seq_unit': [1,2,3,4]
            }
        }
        self.deserialized_data = self.source_object
        self.serialized_data = {
            'int_unit': 123,
            'nested_dict_schema': {
                'int_unit': 123,
                'str_unit': 'Some string',
                'str_seq_unit': ['string1', 'string2'],
                'int_seq_unit': [1,2,3,4]
            }
        }
        self.object_to_sync = {}
        self.expected_synced_object = self.source_object

    def test_serialize_ok(self):
        schema = TestMappingSchemaNested1(object=self.source_object)
        self.assertDictEqual(dict(schema.serialize()), self.serialized_data)

    def test_deserialize_ok(self):
        schema = TestMappingSchemaNested1(data=self.serialized_data)
        self.assertDictEqual(dict(schema.deserialize()), self.deserialized_data)

    def test_sync(self):
        schema = TestMappingSchemaNested1(
            object=self.object_to_sync,
            data=self.serialized_data)
        self.assertTrue(schema.is_valid())
        schema.sync()
        self.assertDictEqual(self.object_to_sync, self.expected_synced_object)


class TestObjectMappingSchemaCase(unittest.TestCase):
    def setUp(self):
        self.source_object = TestMappingObject(
            int_unit=123,
            str_unit='Some string',
            str_seq_unit=['string1', 'string2'],
            int_seq_unit=[1,2,3,4]
        )
        self.serialized_data = {
            'int_unit': 123,
            'str_unit': 'Some string',
            'str_seq_unit': ['string1', 'string2'],
            'int_seq_unit': [1, 2, 3, 4]
        }
        self.deserialized_data = self.serialized_data
        self.object_to_sync = TestMappingObject()
        self.expected_synced_object = self.source_object

    def test_serialize_ok(self):
        schema = TestObjectSchema(object=self.source_object)
        self.assertDictEqual(dict(schema.serialize()), self.serialized_data)

    def test_deserialize_ok(self):
        schema = TestObjectSchema(data=self.serialized_data)
        self.assertDictEqual(dict(schema.deserialize()), self.deserialized_data)

    def test_sync(self):
        schema = TestObjectSchema(
            object=self.object_to_sync, data=self.serialized_data)
        schema.is_valid()
        schema.sync()
        self.assertDictEqual(
            self.object_to_sync.__dict__,
            self.source_object.__dict__)

    # def test_metadata(self):
    #     schema = TestObjectSchema()
    #     print dict(determine_metadata(schema))