from marshmallow import Schema, fields

class ChargeSchema(Schema):
    provision_id = fields.String(required=True, attribute="provision")
    charge_type = fields.String(required=True, attribute="charge-type")
    geometry_description = fields.String(required=True, attribute="description")
    geometry = fields.String(required=True, attribute="geometry")
    originating_authority_id = fields.String(required=True, attribute="originating-authority")

    authority_charge_id = fields.String(required=False, attribute="authority-charge-id")
    creation_date = fields.Date(required=False, attribute="creation-date")
    expiration_date = fields.Date(required=False, attribute="expiration-date")
    instrument = fields.String(required=False, attribute="instrument")
    migrating_authority = fields.String(required=False, attribute="migrating-authority")
    old_register_part = fields.String(required=False, attribute="old-register-part")
    place_of_inspection = fields.String(required=False, attribute="place-of-inspection")
    inspection_reference = fields.String(required=False, attribute="inspection-reference")

class PlaceOfInspectionSchema(Schema):
    location = fields.String(required=True, attribute="location")

class AuthoritySchema(Schema):
    name = fields.String(required=True, attribute="name")

class ProvisionSchema(Schema):
    description = fields.String(required=True, attribute="description")
