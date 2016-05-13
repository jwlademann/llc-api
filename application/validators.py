from marshmallow import Schema, fields

class ChargeSchema(Schema):
    provision_id = fields.String(required=True, load_from="provision")
    charge_type = fields.String(required=True, load_from="charge-type")
    geometry_description = fields.String(required=True, load_from="description")
    geometry = fields.String(required=True, load_from="geometry")
    originating_authority_id = fields.String(required=True, load_from="originating-authority")

    authority_charge_id = fields.String(required=False, load_from="authority-charge-id")
    creation_date = fields.String(required=False, load_from="creation-date")
    expiration_date = fields.String(required=False, load_from="expiration-date")
    instrument = fields.String(required=False, load_from="instrument")
    migrating_authority = fields.String(required=False, load_from="migrating-authority")
    old_register_part = fields.String(required=False, load_from="old-register-part")
    place_of_inspection = fields.String(required=False, load_from="place-of-inspection")
    inspection_reference = fields.String(required=False, load_from="inspection-reference")

class PlaceOfInspectionSchema(Schema):
    location = fields.String(required=True, load_from="location")

class AuthoritySchema(Schema):
    name = fields.String(required=True, load_from="name")

class ProvisionSchema(Schema):
    description = fields.String(required=True, load_from="description")
