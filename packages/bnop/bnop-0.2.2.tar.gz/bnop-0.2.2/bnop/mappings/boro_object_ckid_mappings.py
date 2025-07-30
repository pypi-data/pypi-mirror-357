from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)


class BoroObjectCkIdToBnopMappings(
    object
):
    registry_keyed_on_ckid = {}
    registry_keyed_on_bnop = {}

    def __init__(
        self,
        boro_object_ckid: BoroObjectCkIds,
        bnop_object: BnopObjects,
    ):
        self.ckid = boro_object_ckid

        self.bnop_object = bnop_object

        self.registry_keyed_on_ckid.update(
            {
                self.ckid: self.bnop_object
            }
        )

        self.registry_keyed_on_bnop.update(
            {
                self.bnop_object: self.ckid
            }
        )

    @staticmethod
    def get_bnop_type(
        boro_object_ckid: BoroObjectCkIds,
    ):
        bnop_object = BoroObjectCkIdToBnopMappings.registry_keyed_on_ckid[
            boro_object_ckid
        ]

        return bnop_object

    @staticmethod
    def get_ckid(
        bnop_object: BnopObjects,
    ):
        boro_object_ckid = BoroObjectCkIdToBnopMappings.registry_keyed_on_bnop[
            bnop_object
        ]

        return boro_object_ckid
