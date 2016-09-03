# coding: utf-8

import pytest
from jsonschema.exceptions import ValidationError

import JSONSchemaOOP


class TestJSONType:
    @pytest.mark.parametrize(('parameters', 'expected'), [
        ({}, {'type': 'number'}),
        ({'minimum': 1}, {'type': 'number', 'minimum': 1}),
        ({'maximum': 2}, {'type': 'number', 'maximum': 2}),
        ({'multiple_of': 2}, {'type': 'number', 'multipleOf': 2}),

        (
            {'minimum': 1, 'maximum': 4, 'multiple_of': 2},
            {'type': 'number', 'minimum': 1, 'maximum': 4, 'multipleOf': 2}
        ),
    ])
    def test_json_number(self, parameters, expected):
        inst = JSONSchemaOOP.JSONNumber(**parameters)

        inst_obj = inst.render()

        assert inst_obj == expected

    @pytest.mark.parametrize(('parameters', 'expected'), [
        ({}, {'type': 'string'}),
        ({'min_length': 1}, {'type': 'string', 'minLength': 1}),
        ({'max_length': 10}, {'type': 'string', 'maxLength': 10}),
        ({'pattern': '\\d'}, {'type': 'string', 'pattern': '\\d'}),

        (
            {'min_length': 1, 'max_length': 10, 'pattern': '\\d'},
            {'type': 'string', 'minLength': 1, 'maxLength': 10, 'pattern': '\\d'}
        ),
    ])
    def test_json_string(self, parameters, expected):
        inst = JSONSchemaOOP.JSONString(**parameters)

        inst_obj = inst.render()

        assert inst_obj == expected

    @pytest.mark.parametrize(('parameters', 'expected'), [
        ({}, {'type': 'array'}),
        ({'items': [JSONSchemaOOP.JSONString()]}, {'items': [{'type': 'string'}], 'type': 'array'}),
        ({'unique_items': True}, {'uniqueItems': True, 'type': 'array'}),
        ({'min_items': True}, {'minItems': True, 'type': 'array'}),
        ({'max_items': True}, {'maxItems': True, 'type': 'array'}),

        (
            {'min_items': 1, 'max_items': 10, 'unique_items': True, 'items': [JSONSchemaOOP.JSONString()]},
            {'minItems': 1, 'maxItems': 10, 'uniqueItems': True, 'items': [{'type': 'string'}], 'type': 'array'}
        ),
    ])
    def test_json_array(self, parameters, expected):
        inst = JSONSchemaOOP.JSONArray(**parameters)

        inst_obj = inst.render()

        assert inst_obj == expected

    @pytest.mark.parametrize(('parameters', 'expected'), [

        ({}, {'type': 'object'}),
        (
            {'properties': {'name': JSONSchemaOOP.JSONString()}},
            {'type': 'object', 'properties': {'name': {'type': 'string'}}}
        ),
        (
            {'properties': {'name': JSONSchemaOOP.JSONString()}, 'required': ['name']},
            {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'required': ['name']}
        ),
        (
            {'properties': {'name': JSONSchemaOOP.JSONString()}, 'min_properties': 1},
            {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'minProperties': 1}
        ),
        (
            {'properties': {'name': JSONSchemaOOP.JSONString()}, 'max_properties': 10},
            {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'maxProperties': 10}
        ),

        (
            {'properties': {'name': JSONSchemaOOP.JSONString()}, 'min_properties': 1, 'max_properties': 10},
            {'type': 'object', 'properties': {'name': {'type': 'string'}}, 'minProperties': 1, 'maxProperties': 10}
        ),
    ])
    def test_json_object(self, parameters, expected):
        inst = JSONSchemaOOP.JSONObject(**parameters)

        inst_obj = inst.render()

        assert inst_obj == expected

    def test_json_schema_reference(self):
        inst = JSONSchemaOOP.JSONSchemaReference('my-reference')

        assert inst.render() == {'$ref': '#/definitions/my-reference'}

    def test_json_null(self):
        inst = JSONSchemaOOP.JSONNull()

        assert inst.render() == {'type': 'null'}

    def test_json_boolean(self):
        inst = JSONSchemaOOP.JSONBoolean()

        assert inst.render() == {'type': 'boolean'}

    def test_json_schema(self):
        class MySchema(JSONSchemaOOP.JSONSchema):
            properties = {
                'name': JSONSchemaOOP.JSONString()
            }

        inst = MySchema()

        inst_obj = inst.render()
        expected = {
            'type': 'object',
            'properties': {'name': {'type': 'string'}},
            'schema': 'http://json-schema.org/draft-04/schema#'
        }

        assert inst_obj == expected


class AddressJSONSchemaObject(JSONSchemaOOP.JSONObject):
    required = ['street', 'street_number', 'zip', 'city']
    properties = {
        'street': JSONSchemaOOP.JSONString(),
        'street_number': JSONSchemaOOP.JSONString(),
        'zip': JSONSchemaOOP.JSONNumber(),
        'city': JSONSchemaOOP.JSONString(),
    }


class AddressJSONSchemaObjectV2(AddressJSONSchemaObject):
    def required_remove(self):
        return ['city']

    def properties_remove(self):
        return ['city']


class AddressJSONSchemaObjectV3(AddressJSONSchemaObjectV2):
    def required_add(self):
        return ['location']

    def properties_add(self):
        return {'location': JSONSchemaOOP.JSONString()}


class TestJSONObjectInheritance(object):
    def test_inherit_json_object(self):
        inst = AddressJSONSchemaObject()

        inst_obj = inst.render()

        expected = {
            'required': ['street', 'street_number', 'zip', 'city'],
            'type': 'object',
            'properties': {
                'city': {'type': 'string'},
                'street': {'type': 'string'},
                'street_number': {'type': 'string'},
                'zip': {'type': 'number'}
            }
        }

        assert inst_obj == expected

    def test_inherit_json_object_removes_attributes(self):
        inst = AddressJSONSchemaObjectV2()

        expected = {
            'required': ['street', 'street_number', 'zip'],
            'type': 'object',
            'properties': {
                'street': {'type': 'string'},
                'street_number': {'type': 'string'},
                'zip': {'type': 'number'}
            }
        }

        inst_obj = inst.render()

        assert inst_obj == expected

    def test_inherit_json_object_adds_attributes(self):
        inst = AddressJSONSchemaObjectV3()

        expected = {
            'required': ['street', 'zip', 'street_number', 'location'],
            'type': 'object',
            'properties': {
                'street': {'type': 'string'},
                'street_number': {'type': 'string'},
                'zip': {'type': 'number'},
                'location': {'type': 'string'}
            }
        }

        inst_obj = inst.render()

        assert inst_obj == expected


class TestFullJSONSchema(object):
    @pytest.mark.parametrize(('data', 'is_valid'), [
        ({'address': {'street': 'musterstreet', 'street_number': '12 a', 'zip': 12345, 'location': 'Berlin'}}, True),

        # Errors
        ({'address': {}}, False),
        ({'address': 'haha'}, False),
        ({'address': {'street': 'musterstreet'}}, False),
        ({'address': {'street': 'musterstreet', 'street_number': '12 a'}}, False),
        ({'address': {'street': 'musterstreet', 'street_number': '12 a', 'zip': 'a125', }}, False),
        ({'address': {'street': 'musterstreet', 'street_number': '12 a', 'zip': 'a125', 'location': 'Berlin'}}, False),
    ])
    def test_address_full_schema(self, data, is_valid):
        class MySchema(JSONSchemaOOP.JSONSchema):
            properties = {
                'address': JSONSchemaOOP.JSONSchemaReference('address')
            }
            definitions = {
                'address': AddressJSONSchemaObjectV3()
            }

        inst = MySchema()

        inst_obj = inst.render()
        expected = {
            'schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {
                'address': {'$ref': '#/definitions/address'}
            },
            'definitions': {
                'address': {
                    'required': ['street', 'zip', 'street_number', 'location'],
                    'type': 'object',
                    'properties': {
                        'street': {'type': 'string'},
                        'street_number': {'type': 'string'},
                        'zip': {'type': 'number'},
                        'location': {'type': 'string'}
                    }
                }
            },
        }

        assert inst_obj == expected

        if is_valid:
            inst.validate(data)
        else:
            with pytest.raises(ValidationError):
                inst.validate(data)
