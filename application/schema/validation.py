local_land_charge_schema = {
    "title": "local-land-charge schema",
    "type": "object",
    "properties": {
        "provision": {
            "type": "string",
            "pattern": "\S+"
        },
        "charge-type": {
            "type": "string",
            "pattern": "\S+"
        },
        "description": {
            "type": "string",
            "pattern": "\S+"
        },
        "geometry": {
            "type": "object",
            "pattern": "\S+"
        },
        "originating-authority": {
            "type": "string",
            "pattern": "\S+"
        },
        "authority-charge-id": {
            "type": "string"
        },
        "creation-date": {
            "type": "string"
        },
        "expiration-date": {
            "type": "string"
        },
        "instrument": {
            "type": "string"
        },
        "migrating-authority": {
            "type": "string"
        },
        "old-register-part": {
            "type": "string"
        },
        "place-of-inspection": {
            "type": "string"
        },
        "inspection-reference": {
            "type": "string"
        },
        "land-description": {
            "type": "string"
        },
        "work-particulars": {
            "type": "string"
        },
        "capacity-description": {
            "type": "string"
        },
        "compensation-paid": {
            "type": "string"
        },
        "unique-property-reference-number": {
            "type": "string"
        },
        "archived": {
            "type": "boolean"
        }
    },
    "additionalProperties": False,
    "required": ["provision", "charge-type", "description", "geometry", "originating-authority"]
}

llc_place_of_inspection_schema = {
    "title": "llc-place-of-inspection schema",
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "pattern": "\S+"
        },
        "archived": {
            "type": "boolean"
        }
    },
    "additionalProperties": False,
    "required": ["location"]
}

statutory_provision_schema = {
    "title": "statutory-provision schema",
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
            "pattern": "\S+"
        },
        "archived": {
            "type": "boolean"
        }
    },
    "additionalProperties": False,
    "required": ["description"]
}

llc_registering_authority_schema = {
    "title": "llc-registering-authority schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": "\S+"
        },
        "archived": {
            "type": "boolean"
        }
    },
    "additionalProperties": False,
    "required": ["name"]
}
