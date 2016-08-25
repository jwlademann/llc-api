from application import register_utils, app
import jsonschema


LAND_COMP_ACT_S8 = '{} {} {}'.format(app.config['LAND_COMP_ACT_S8_INSTRUMENT'],
                                     app.config['LAND_COMP_ACT_S8_YEAR'],
                                     app.config['LAND_COMP_ACT_S8_PROVISION'])
LAND_COMP_ACT_S52 = '{} {} {}'.format(app.config['LAND_COMP_ACT_S52_INSTRUMENT'],
                                      app.config['LAND_COMP_ACT_S52_YEAR'],
                                      app.config['LAND_COMP_ACT_S52_PROVISION'])


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
    errors = []
    if 'statutory-provisions' in json_payload:
        for stat_prov in json_payload['statutory-provisions']:
            try:
                record = register_utils.retrieve_curie(stat_prov)
            except Exception as e:
                errors.append(str(e))
                record = None
            if not record:
                errors.append("Failed to retrieve statutory provision '{}' for {} validation".format(stat_prov, LAND_COMP_ACT_S8))
            elif 'provision' not in record and 'statutory-instrument' not in record and 'year' not in record:
                errors.append("Invalid statutory provision '{}' for {} validation".format(stat_prov, LAND_COMP_ACT_S8))
            elif '{} {} {}'.format(record['statutory-instrument'], record['year'], record['provision']).lower() == LAND_COMP_ACT_S8.lower():
                s8_provision = True
                break
    if s8_provision and not s8_schema:
        errors.append("Charges with {} provision must conform to land-compensation-charge-s8 definition".format(LAND_COMP_ACT_S8))
    elif not s8_provision and s8_schema:
        errors.append("Charges which conform to land-compensation-charge-s8 definition must contain {} provision".format(LAND_COMP_ACT_S8))
    return {'errors': errors}


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
    errors = []
    if 'statutory-provisions' in json_payload:
        for stat_prov in json_payload['statutory-provisions']:
            try:
                record = register_utils.retrieve_curie(stat_prov)
            except Exception as e:
                errors.append(str(e))
                record = None
            if not record:
                errors.append("Failed to retrieve statutory provision '{}' for {} validation".format(stat_prov, LAND_COMP_ACT_S52))
            elif 'provision' not in record and 'statutory-instrument' not in record and 'year' not in record:
                errors.append("Invalid statutory provision '{}' for {} validation".format(stat_prov, LAND_COMP_ACT_S52))
            elif '{} {} {}'.format(record['statutory-instrument'], record['year'], record['provision']).lower() == LAND_COMP_ACT_S52.lower():
                s52_provision = True
                break
    if s52_provision and not s52_schema:
        errors.append("Charges with {} provision must conform to land-compensation-charge-s52 definition".format(LAND_COMP_ACT_S52))
    elif not s52_provision and s52_schema:
        errors.append("Charges which conform to land-compensation-charge-s52 definition must contain {} provision".format(LAND_COMP_ACT_S52))
    return {'errors': errors}


def validate_instrument_provisions(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Additional check for either instrument or statutory-provisions
    """
    if 'instrument' not in json_payload and ('statutory-provisions' not in json_payload or len(json_payload['statutory-provisions']) == 0):
        return {'errors': ["At least one of 'statutory-provisions' or 'instrument' must be supplied."]}
    return {'errors': []}


def validate_statutory_provisions(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Additional checks for the statutory provisions
    """
    errors = []
    if 'statutory-provisions' in json_payload and json_payload['statutory-provisions']:
        for stat_prov in json_payload['statutory-provisions']:
            try:
                record = register_utils.retrieve_curie(stat_prov)
            except Exception as e:
                errors.append(str(e))
                record = None
            if not record:
                errors.append("Failed to retrieve statutory provision '{}' for statutory provision validation".format(stat_prov))
            elif 'provision' not in record and 'statutory-instrument' not in record and 'year' not in record:
                errors.append("Invalid statutory provision '{}' for statutory provision validation".format(stat_prov))
            elif method.lower() == 'post' and 'end-date' in record and record['end-date']:
                errors.append("New charges cannot use archived statutory provision '{}'".format(stat_prov))
            elif method.lower() == 'put' and 'end-date' in record and record['end-date']:
                try:
                    pri_id = register_utils.REGISTER_INFO[sub_domain]['primary-id']
                    record = register_utils.retrieve_curie("{}:{}".format(sub_domain, json_payload[pri_id]))
                except Exception as e:
                    errors.append(str(e))
                    record = None
                if not record:
                    errors.append("Could not retrieve record '{}:{}' for statutory provision validation".format(sub_domain, json_payload[pri_id]))
                elif 'statutory-provisions' not in record or stat_prov not in record['statutory-provisions']:
                    errors.append("Cannot add archived statutory provision '{}'".format(stat_prov))
    return {'errors': errors}


def validate_registration_date(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Validate that registration date is unaltered/not supplied for updates
    """
    errors = []
    if method.lower() == 'put':
        try:
            pri_id = register_utils.REGISTER_INFO[sub_domain]['primary-id']
            record = register_utils.retrieve_curie("{}:{}".format(sub_domain, json_payload[pri_id]))
        except Exception as e:
            errors.append(str(e))
            record = None
        if 'registration-date' not in json_payload:
            if not record:
                errors.append("Could not retrieve record '{}:{}' for update validation".format(sub_domain, json_payload[pri_id]))
            elif 'registration-date' not in record:
                errors.append("Existing record has no 'registration-date', cannot update")
            else:
                json_payload['registration-date'] = record['registration-date']
                app.logger.warn("'registration-date' not included in update, using value from previous version for record '{}:{}'".format(sub_domain,
                                                                                                                                          json_payload[pri_id]))
        elif ('registration-date' in json_payload and 'registration-date' in record and (json_payload['registration-date'] != record['registration-date'])) or \
             ('registration-date' in json_payload and 'registration-date' not in record):
            errors.append("Cannot update field 'registration-date'")
    return {'errors': errors}


def validate_further_information(sub_domain, end_point, end_point_pattern, method, json_payload):
    """Validate uniqueness of further information
    """
    errors = []
    if 'further-information' in json_payload and json_payload['further-information']:
        locations = [x['information-location'] for x in json_payload['further-information']]
        if len(locations) != len(set(locations)):
            errors.append("Further information locations must be unique")
    return {'errors': errors}
