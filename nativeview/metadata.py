from collections import OrderedDict

import unit_types
import validators


def handle_basic(unit, only_type=False):
    result = OrderedDict()
    result['type'] = lookup_type(unit)

    if only_type:
        return result

    result['required'] = unit.required
    result['read_only'] = unit.read_only

    if unit.validator and hasattr(unit.validator, 'get_metadata'):
        result.update(unit.validator.get_metadata())

    return result


def handle_with_children(unit, only_type=False):
    result = handle_basic(unit, only_type)
    fields = result['fields'] = OrderedDict()

    children_only_type = unit.read_only
    for name, child in unit.children.iteritems():
        fields[name] = determine_metadata(child, only_type=children_only_type)

    return result


handlers_lookup = {
    unit_types.Integer: handle_basic,
    unit_types.String: handle_basic,
    unit_types.Date: handle_basic,
    unit_types.DateTime: handle_basic,
    unit_types.Mapping: handle_with_children,
    unit_types.ObjectMapping: handle_with_children,
}

def lookup_handler(unit):
    for cls, handler in handlers_lookup.iteritems():
        if isinstance(unit.type, cls):
            return handler

    raise KeyError(unit.type)


types_lookup = {
    unit_types.Integer: 'integer',
    unit_types.String: 'string',
    unit_types.Date: 'string',
    unit_types.DateTime: 'string',
    unit_types.Mapping: 'dictionary',
    unit_types.ObjectMapping: 'dictionary',
}

def lookup_type(unit):
    for cls, type in types_lookup.iteritems():
        if isinstance(unit.type, cls):
            return type

    raise KeyError(unit.type)


def determine_metadata(unit, only_type=False):
    return lookup_handler(unit)(unit, only_type)
