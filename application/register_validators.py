from application import register_utils


def validate_primary_id(sub_domain, end_point, end_point_pattern, method, json_payload):
    if method.lower() == 'put':
        pri_id = register_utils.REGISTER_INFO[sub_domain]['primary-id']
        if pri_id not in json_payload or (end_point.split("/")[-1] != json_payload[pri_id]):
            return {"errors": ["Primary identifier in URI must match key '" + pri_id + "' in json"]}
    return {"errors": []}


def validate_archive_update(sub_domain, end_point, end_point_pattern, method, json_payload):
    errors = []
    if method.lower() == 'put':
        try:
            pri_id = register_utils.REGISTER_INFO[sub_domain]['primary-id']
            record = register_utils.retrieve_curie("{}:{}".format(sub_domain, json_payload[pri_id]))
        except Exception as e:
            errors.append(str(e))
            record = None
        if not record:
            errors.append("Could not retrieve record '{}:{}' for update validation".format(sub_domain, json_payload[pri_id]))
        elif 'end-date' in record and record['end-date']:
            errors.append("Record has been archived, cannot update")
    return {"errors": errors}
