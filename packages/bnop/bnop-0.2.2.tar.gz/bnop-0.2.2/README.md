# BNOP - BORO Native Objects (Python)

BNOP is a comprehensive ontology library implementing the BORO (Business Object Reference Ontology) approach to information modeling in Python. This library provides a robust framework for creating, managing, and serializing ontological objects and their relationships.

## Overview

BNOP is a reference implementation containing the code for the BORO Native Objects (Python) Domain. This is a fork of the [original BNOP library created by BORO Solutions](https://github.com/boro-alpha/bnop), adapted for use within the bCLEARer Platform Development Kit (PDK).

BORO is a foundational ontology that provides a rigorous top-level structure for information modeling. It uses a 4D (four-dimensional) perspective where objects persist through time and have temporal parts.

## Library Structure

The BNOP library is organized into several key components:

### 1. Core Object Model

Located in `/bnop/core/object_model/`, this module contains the fundamental BNOP object classes:

- **BnopObjects**: The base class for all BNOP entities, maintaining registries of objects keyed by UUID and type
- **BnopTypes**: Represents ontological types that can classify instances
- **BnopNames**: Implements naming concepts for objects
- **BnopTuples**: Represents relationships between objects (e.g., type-instance, supertype-subtype)
- **BnopElements**: Basic elements in the ontology
- **BnopPlaceableTypes**: Types that can be placed in specific positions in tuples
- **BnopTypePlaces**: Defines positions in tuples for specific types

Each object maintains its relationships with other objects through sets like `types`, `instances`, `supertypes`, `subtypes`, etc.

### 2. Factory Classes

Located in `/bnop/core/factories/`, these classes provide methods for creating different types of BNOP objects:

- **BnopObjectFactories**: Creates basic objects
- **BnopTypeFactories**: Creates type objects
- **BnopNameFactories**: Creates name objects
- **BnopTupleFactories**: Creates relationship tuples
- **BnopElementFactories**: Creates elements
- **BnopPlaceableTypeFactories**: Creates placeable types
- **BnopTypePlaceFactories**: Creates type places

The factory pattern ensures consistent object creation with proper registration in the object registries.

### 3. Infrastructure

Located in `/bnop/infrastructure/`, this module provides utility classes:

- **names.py**: Utilities for working with names
- **translators.py**: Translators between different representations

### 4. Input/Output

Located in `/bnop/bnop_io/`, this module handles persistence of BNOP objects:

- **shelve_bnop.py**: Provides functions to save and load BNOP objects using Python's shelve module

### 5. Migrations

Located in `/bnop/migrations/`, this module includes functionality for format conversions:

- **bnop_to_xml_migration**: Contains classes to convert BNOP objects to XML representation
  - **bnop_xml_write_orchestrator.py**: Orchestrates the XML export process
  - **adders**: Contains classes that add specific object types to XML
  - **sorters**: Sorts objects for consistent XML output

### 6. Facades

The `BnopFacades` class (`/bnop/bnop_facades.py`) provides a simplified interface for common operations:

- Creating various types of BNOP objects (objects, types, names, tuples, etc.)
- Establishing relationships between objects
- Serializing BNOP objects to XML

## Basic Usage

### Creating Objects and Types

```python
from bnop.bnop_facades import BnopFacades
from bclearer_orchestration_services.identification_services.uuid_service.uuid_helpers.uuid_factory import create_new_uuid

# Create repository UUID
repository_uuid = create_new_uuid()

# Create a simple object
object_uuid = create_new_uuid()
my_object = BnopFacades.create_bnop_object(
    object_uuid,
    repository_uuid,
    presentation_name="Example Object"
)

# Create a type
type_uuid = create_new_uuid()
my_type = BnopFacades.create_bnop_type(
    type_uuid,
    repository_uuid,
    presentation_name="Example Type"
)

# Create a name
name_uuid = create_new_uuid()
my_name = BnopFacades.create_bnop_name(
    name_uuid,
    "ExampleName",
    repository_uuid
)
```

### Creating Relationships

```python
from bclearer_core.ckids.boro_object_ckids import BoroObjectCkIds

# Create a type-instance relationship
type_instance_tuple = BnopFacades.create_bnop_tuple_from_two_placed_objects(
    create_new_uuid(),
    my_type,             # Type at place 1
    my_object,           # Instance at place 2
    BoroObjectCkIds.TypesInstances,
    repository_uuid
)

# Create a naming relationship
naming_tuple = BnopFacades.create_bnop_tuple_from_two_placed_objects(
    create_new_uuid(),
    my_name,             # Name at place 1
    my_object,           # Named object at place 2
    BoroObjectCkIds.NamedBy,
    repository_uuid
)

# Create a supertype-subtype relationship
supertype_tuple = BnopFacades.create_bnop_tuple_from_two_placed_objects(
    create_new_uuid(),
    my_type,             # Supertype at place 1
    another_type,        # Subtype at place 2
    BoroObjectCkIds.SuperSubTypes,
    repository_uuid
)
```

### Persistent Storage

```python
# Export to XML
BnopFacades.write_bnop_object_to_xml("output.xml")

# Using shelve for persistence
from bnop.bnop_io.shelve_bnop import write_bnop, read_bnop

# Save objects
write_bnop("bnop_data")

# Load and view objects
read_bnop("bnop_data")
```

## Key Concepts

### Object Registry

BNOP maintains two global registries:
- `BnopObjects.registry_keyed_on_uuid`: All objects indexed by UUID
- `BnopObjects.registry_keyed_on_ckid_type`: Objects indexed by their BORO classification

### Naming and Identity

- Every BNOP object has a UUID for identity
- Objects can be associated with names via `NamedBy` relationships
- Names are themselves objects with exemplar representations (the text value)

### Tuples and Relationships

Tuples represent relationships between objects:
- `TypesInstances`: Relates types to their instances
- `SuperSubTypes`: Establishes type hierarchies
- `NamedBy`: Connects names to the objects they name

### Placeable Types and Type Places

BNOP supports complex relationship modeling through:
- Placeable types that can occupy positions in tuples
- Type places that define which types can go in which positions

## Usage Examples

For examples, refer to the Boson project:
- https://github.com/boro-alpha/bclearer_boson_1_1.git

## Documentation Policy

Following the BORO documentation policy and principles from Robert C. Martin's "Clean Code," this library aims to be self-documenting through clean, expressive code.

## Execution

This code is intended to be used as a library rather than run standalone.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgements

This work was developed initially by BORO Solutions (https://www.borosolutions.net/) and was updated as part of the Information Management Framework to support the [National Digital Twin programme](https://www.cdbb.cam.ac.uk/what-we-do/national-digital-twin-programme), and funded by [Department for Business, Energy & Industrial Strategy](https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy) through the Centre for the Protection of National Infrastructure.
It is being used here as the core upper ontology in the Ontoledgy bclearer pdk.
