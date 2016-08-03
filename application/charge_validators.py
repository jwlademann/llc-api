from application import register_utils
import jsonschema


def validate_s8_compensation_charge(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Additional validation for s8 compensation charge
    """
    try:
        jsonschema.validate(json_payload, {"$ref": "local-land-charge.json#/definitions/land-compensation-charge-s8"},
                            resolver=register_utils.RELATIVE_RESOLVER)
        s8_schema = True
    except jsonschema.ValidationError as e:
        s8_schema = False
    s8_provision = False
    if 'statutory-provisions' in json_payload:
        for stat_prov in json_payload['statutory-provisions']:
            try:
                record = register_utils.retrieve_curie(stat_prov)
            except Exception as e:
                return {"errors": [str(e)]}
            if not record:
                return {"errors": ["Failed to retrieve statutory provision for Land Compensation Act 1973 section 8(4) validation"]}
            if 'text' not in record:
                return {"errors": ["Invalid statutory provision for Land Compensation Act 1973 section 8(4) validation"]}
            if record['text'].lower() == "Land Compensation Act 1973 section 8(4)".lower():
                s8_provision = True
                break
    if s8_provision and not s8_schema:
        return {'errors': ["Charges with Land Compensation Act 1973 section 8(4) provision must conform to land-compensation-charge-s8 definition"]}
    if not s8_provision and s8_schema:
        return {'errors': ["Charges which conform to land-compensation-charge-s8 definition must contain Land Compensation Act 1973 section 8(4) provision"]}
    return {'errors': []}


def validate_s52_compensation_charge(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Additional validation for s52 compensation charge
    """
    try:
        jsonschema.validate(json_payload, {"$ref": "local-land-charge.json#/definitions/land-compensation-charge-s52"},
                            resolver=register_utils.RELATIVE_RESOLVER)
        s52_schema = True
    except jsonschema.ValidationError as e:
        s52_schema = False
    s52_provision = False
    if 'statutory-provisions' in json_payload:
        for stat_prov in json_payload['statutory-provisions']:
            try:
                record = register_utils.retrieve_curie(stat_prov)
            except Exception as e:
                return {"errors": [str(e)]}
            if not record:
                return {"errors": ["Failed to retrieve statutory provision for Land Compensation Act 1973 section 52(8) validation"]}
            if 'text' not in record:
                return {"errors": ["Invalid statutory provision for Land Compensation Act 1973 section 52(8) validation"]}
            if record['text'].lower() == "Land Compensation Act 1973 section 52(8)".lower():
                s52_provision = True
                break
    if s52_provision and not s52_schema:
        return {'errors': ["Charges with Land Compensation Act 1973 section 52(8) provision must conform to land-compensation-charge-s52 definition"]}
    if not s52_provision and s52_schema:
        return {'errors': ["Charges which conform to land-compensation-charge-s52 definition must contain Land Compensation Act 1973 section 52(8) provision"]}
    return {'errors': []}


def validate_instrument_provisions(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Additional check for either instrument or statutory-provisions
    """
    if 'instrument' not in json_payload and ('statutory-provisions' not in json_payload or len(json_payload['statutory-provisions']) == 0):
        return {'errors': ["At least one of 'statutory-provisions' or 'instrument' must be supplied."]}
    return {'errors': []}
