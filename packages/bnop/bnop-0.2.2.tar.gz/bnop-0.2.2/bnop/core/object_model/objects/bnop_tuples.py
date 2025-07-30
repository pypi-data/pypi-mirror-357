from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)
from bnop.core.object_model.objects.places.bnop_placed_objects_dictionaries import (
    BnopPlacedObjectsDictionaries,
)


class BnopTuples(BnopObjects):

    def __init__(
        self,
        uuid,
        tuple_placed_objects_dictionary: BnopPlacedObjectsDictionaries,
        immutable_minor_composition_couple_type_boro_object_ckid: BoroObjectCkIds,
        owning_repository_uuid,
    ):
        BnopObjects.__init__(
            self,
            uuid,
            owning_repository_uuid,
        )

        self.add_to_registry_keyed_on_ckid_type(
            immutable_minor_composition_couple_type_boro_object_ckid
        )

        self.immutable_minor_composition_couple_type_boro_object_ckid = immutable_minor_composition_couple_type_boro_object_ckid

        self.tuple_placed_objects_dictionary = tuple_placed_objects_dictionary
