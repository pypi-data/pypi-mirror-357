from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)


def translate_to_uuids(
    bnop_objects: set,
):
    object_uuids = set()

    for bnop_object in bnop_objects:
        object_uuids.add(
            bnop_object.uuid
        )

    return object_uuids


def translate_to_objects(
    bnop_object_uuids: set,
):
    objects = set()

    for (
        bnop_object_uuid
    ) in bnop_object_uuids:
        objects.add(
            BnopObjects.registry_keyed_on_uuid[
                bnop_object_uuid
            ]
        )

    return objects
