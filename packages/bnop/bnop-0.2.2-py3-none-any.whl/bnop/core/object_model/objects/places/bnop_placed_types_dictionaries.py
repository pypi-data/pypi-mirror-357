from bclearer_core.ckids.place_number_type_ckids import (
    PlaceNumberTypeCkIds,
)
from bnop.core.object_model.objects.bnop_types import (
    BnopTypes,
)


class BnopPlacedTypesDictionaries(
    object
):

    def __init__(self):
        self._placed_types_dictionary = (
            {}
        )

    def add_placed_type_to_dictionary(
        self,
        placing_ckid: PlaceNumberTypeCkIds,
        relation_placed_type: BnopTypes,
    ):
        self._placed_types_dictionary[
            placing_ckid
        ] = relation_placed_type

    def try_get_placed_type_for_place_number_ckid(
        self,
        placing_ckid: PlaceNumberTypeCkIds,
    ):
        placed_type = self._placed_types_dictionary[
            placing_ckid
        ]

        return placed_type
