from marshmallow import Schema, fields

class ChargeSchema(Schema):
    provision_id = fields.Integer(required=True)
    creation_date = fields.Date(required=True)
    charge_type = fields.String(required=True)
    geometry_description = fields.String(required=True)
    geometry = fields.String(required=True)

class FurtherInfoSchema(Schema):
    location = fields.String(required=True)

class AuthoritySchema(Schema):
    name = fields.String(required=True)

class ProvisionSchema(Schema):
    description = fields.String(required=True)
