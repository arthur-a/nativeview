from collections import OrderedDict

import unit_types
import validators


def handle_basic(unit, only_type=False):
    result = OrderedDict()
    result['type'] = types_lookup[unit.type.__class__]

    if only_type:
        return result

    result['required'] = unit.required
    result['read_only'] = unit.read_only

    if isinstance(unit.validator, validators.ChoicesInterface):
        result['choices'] = unit.validator.choices

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


types_lookup = {
    unit_types.Integer: 'integer',
    unit_types.String: 'string',
    unit_types.Date: 'string',
    unit_types.DateTime: 'string',
    unit_types.Mapping: 'dictionary',
    unit_types.ObjectMapping: 'dictionary',
}


def determine_metadata(unit, only_type=False):
    return handlers_lookup[unit.type.__class__](unit, only_type)
