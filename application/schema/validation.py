local_land_charge_schema = {
    "title": "local-land-charge schema",
    "type": "object",
    "properties": {
        "provision": {
            "type": "string"
        },
        "charge-type": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "geometry": {
            "type": "object"
        },
        "originating-authority": {
            "type": "string"
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
        "archived": {
            "type": "boolean"
        }
    },
    "required": ["provision", "charge-type", "description", "geometry", "originating-authority"]
}

llc_place_of_inspection_schema = {
    "title": "llc-place-of-inspection schema",
    "type": "object",
    "properties": {
        "location": {
            "type": "string"
        },
        "archived": {
            "type": "boolean"
        }
    },
    "required": ["location"]
}

statutory_provision_schema = {
    "title": "statutory-provision schema",
    "type": "object",
    "properties": {
        "description": {
            "type": "string"
        },
        "archived": {
            "type": "boolean"
        }
    },
    "required": ["description"]
}

llc_registering_authority_schema = {
    "title": "llc-registering-authority schema",
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "archived": {
            "type": "boolean"
        }
    },
    "required": ["name"]
}
