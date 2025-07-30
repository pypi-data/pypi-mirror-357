from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)


class BnopObjectFactories:
    def __init__(self):
        pass

    @staticmethod
    def create(
        uuid,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        bnop_object = BnopObjects(
            uuid,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        bnop_object.add_to_registry_keyed_on_ckid_type(
            BoroObjectCkIds.Objects
        )

        return bnop_object
