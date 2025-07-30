from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_types import (
    BnopTypes,
)
from bnop.core.object_model.objects.places.bnop_placed_types_dictionaries import (
    BnopPlacedTypesDictionaries,
)


class BnopPlaceableTypes(BnopTypes):

    def __init__(
        self,
        uuid,
        placeable_type_placed_types_dictionary: BnopPlacedTypesDictionaries,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        BnopTypes.__init__(
            self,
            uuid,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        self.add_to_registry_keyed_on_ckid_type(
            BoroObjectCkIds.PlaceableTypes
        )

        self.placeable_type_placed_types_dictionary = placeable_type_placed_types_dictionary
