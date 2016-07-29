from application import register_utils, app


def validate_primary_id(sub_domain, end_point, end_point_pattern, method, json_payload):
    if method.lower() == 'put':
        pri_id = register_utils.REGISTER_INFO[sub_domain]['primary-id']
        if pri_id not in json_payload or (end_point.split("/")[-1] != json_payload[pri_id]):
            return {"errors": ["Primary identifier in URI must match key '" + pri_id + "' in json"]}
    return {"errors": []}
