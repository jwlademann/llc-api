# Local Land Charges Core API

An Application Programming Interface for the Local Land Charges Registration Service. The API receives LLC data in JSON format from either the [llc-frontend]() or through HTTP requests and sends the data on to the [llc-register]().

The API is a Flask/Python application that serves as an Interface to the [llc-register](). The API provides RESTful routes for pushing LLC data to the register.
Data is validated using [JSON Schema](http://json-schema.org) and [RAML](http://raml.org).

## Using the API

The API provides four interfaces to the four registers of the Local Land Charges Service. The API implements the GDS Registers specification, allowing users to create new records and update existing records.

The registers are accessed via HTTP endpoints in the following format:
- Local Land Charges register: `http://local-land-charge/`
- Statutory Provisions register: `http://statutory-provision/`
- Registering Authorities register: `http://llc-registering-authority/`
- Further Information Locations register: `http://further-information-location/`

Each register has two endpoints that can be accessed to perform standard CRUD operations:
- `http://<register-name>/records/`
    - POST: Create a new record in the register, record data is supplied as JSON in the body of the request.
    - GET: Get all the records currently in the register.
- `http://<register-name>/record/<id-number>`
    - GET: Get the record specified by the id-number.
    - PUT: Update the record specified by the id-number, record data is supplied as JSON in the body of the request.
    
The API also has an endpoint for geometry functions to search the Geo-Spatial index on the Local Land Charges Register:
For all functions the geometry data is supplied as GeoJSON in the body of the request.
- `http://local-land-charge/record/geometry/<function>`
    - intersects: Return all geometries whose edges intersect with the supplied geometry.
    - within: Return all geometries that the supplied geometry is completely within.
    - contains: Return all geometries that are completely contained by the supplied geometry.
    - equals: Return all geometries that are exactly equal to the supplied geometry.
    - overlaps: Return all geometries that overlap the supplied geometry.
    - touches: Return all geometries whose edges touch with the supplied geometry.

