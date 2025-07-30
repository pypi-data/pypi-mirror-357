import shelve

from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)


def write_bnop(full_filename: str):
    bnop_shelf = shelve.open(
        full_filename
    )

    bnop_shelf.clear_xml_model_branches()

    for (
        key,
        value,
    ) in (
        BnopObjects.registry_keyed_on_uuid.items()
    ):
        bnop_shelf[key] = value

    bnop_shelf.close()


def read_bnop(full_filename: str):
    bnop_shelf = shelve.open(
        full_filename
    )

    for (
        key,
        value,
    ) in bnop_shelf.items():
        print(
            "Key: "
            + key
            + " - Type: "
            + str(type(value).__name__)
        )

    bnop_shelf.close()
