# Local Land Charges Core API

An Application Programming Interface for the Local Land Charges Registration Service. The API receives LLC data in JSON format from either the [llc-frontend]() or through HTTP requests and sends the data on to the [llc-register]().

The API is a Flask/Python application that serves as an Interface to the [llc-register](). The API provides RESTful routes for pushing LLC data to the register.
Data is validated using [JSON Schema](http://json-schema.org) and [RAML](http://raml.org).

## Contents
- [Local Land Charges Register](#local-land-charges-register)
- [Statutory Provisions Register](#statutory-provisions-register)
- [Registering Authorities Register](#registering-authorities-register)
- [Further Information Location Register](#further-information-location-register)
- [Geo Spatial Search](#geo-spatial-search)
- [Curies](#curies)


## Using the API

The API provides four interfaces to the four registers of the Local Land Charges Service. The API implements the [GDS Registers specification](https://openregister.github.io/specification), allowing users to create new records and update existing records.

## Local Land Charges Register

RAML documentation: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/local-land-charge.json
To create a new Local land charge record it must conform to the following Schema: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/local-land-charge.raml

### Usage

```
GET     local-land-charge/                               -- retrieves all Local Land Charge records currently in the register
GET     local-land-charge/<id-number>                    -- retrieves a specific record by the id number
POST    local-land-charge/records/                       -- creates a new record in the register. Data supplied as JSON reflecting the schema
PUT     local-land-charge/record/<id-number>             -- update the record specified by the id number. Data supplied as JSON reflecting the schema
```


## Statutory Provisions Register

RAML documentation: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/statutory-provision.json
To create a new statutory provision record it must conform to the following Schema: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/statutory-provision.raml

### Usage

```
GET     statutory-provision/                               -- retrieves all Statutory Provision records currently in the register
GET     statutory-provision/<id-number>                    -- retrieves a specific record by the id number
POST    statutory-provision/records/                       -- creates a new record in the register. Data supplied as JSON reflecting the schema
PUT     statutory-provision/record/<id-number>             -- update the record specified by the id number. Data supplied as JSON reflecting the schema
```


## Registering Authorities Register

RAML documentation: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/llc-registering-authority.json
To create a new registering authority record it must conform to the following Schema: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/llc-registering-authority.raml

### Usage

```
GET     llc-registering-authority/                               -- retrieves all Registering Authority records currently in the register
GET     llc-registering-authority/<id-number>                    -- retrieves a specific record by the id number
POST    llc-registering-authority/records/                       -- creates a new record in the register. Data supplied as JSON reflecting the schema
PUT     llc-registering-authority/record/<id-number>             -- update the record specified by the id number. Data supplied as JSON reflecting the schema
```


## Further Information Location Register

RAML documentation: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/further-information-location.json
To create a new further information location record it must conform to the following Schema: http://192.168.249.38/local-land-charges/llc-api/raw/develop/application/static/schema/further-information-location.raml

### Usage

```
GET     further-information-location/                               -- retrieves all Registering Authority records currently in the register
GET     further-information-location/<id-number>                    -- retrieves a specific record by the id number
POST    further-information-location/records/                       -- creates a new record in the register. Data supplied as JSON reflecting the schema
PUT     further-information-location/record/<id-number>             -- update the record specified by the id number. Data supplied as JSON reflecting the schema
```


## Geo Spatial Search

The API also has an endpoint for geometry functions to search the Geo-Spatial index on the Local Land Charges Register:
For all functions the geometry data is supplied as GeoJSON in the body of the request.

It is advised that searches should default to **intersects** as this will return all records that are contained, overlaping or touching the search area.

```
POST    local-land-charge/record/geometry/intersects                -- Return all geometries whose edges intersect with the supplied geometry
POST    local-land-charge/record/geometry/within                    -- Return all geometries that the supplied geometry is completely within
POST    local-land-charge/record/geometry/contains                  -- Return all geometries that are completely contained by the supplied geometry
POST    local-land-charge/record/geometry/equals                    -- Return all geometries that are exactly equal to the supplied geometry
POST    local-land-charge/record/geometry/overlaps                  -- Return all geometries that overlap the supplied geometry
POST    local-land-charge/record/geometry/touches                   -- Return all geometries whose edges touch with the supplied geometry
```



### CURIES

https://www.w3.org/TR/curie/

All records are return with embedded CURIE links. To have the CURIE links resolved an optional **resolve** parameter that can be supplied.
Append one of the above queries with

```
        ?resolve=1                                                  -- Result will have all CURIE links resolved with correct data

```
