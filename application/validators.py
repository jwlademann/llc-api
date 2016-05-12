from marshmallow import Schema, fields

class ChargeSchema(Schema):
    provision_id = fields.String(required=True, attribute="provision")
    charge_type = fields.String(required=True, attribute="charge-type")
    geometry_description = fields.String(required=True, attribute="description")
    geometry = fields.String(required=True, attribute="geometry")
    originating_authority_id = fields.String(required=True, attribute="originating-authority")

class FurtherInfoSchema(Schema):
    location = fields.String(required=True, attribute="location")

class AuthoritySchema(Schema):
    name = fields.String(required=True, attribute="name")

class ProvisionSchema(Schema):
    description = fields.String(required=True, attribute="description")
