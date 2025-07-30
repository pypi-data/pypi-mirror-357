from bclearer_core.ckids.place_number_type_ckids import (
    PlaceNumberTypeCkIds,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)
from bnop.core.object_model.objects.bnop_types import (
    BnopTypes,
)


class BnopTypePlaces(BnopObjects):

    def __init__(
        self,
        uuid,
        placing_type: BnopTypes,
        placed_type: BnopTypes,
        type_place_ckid: PlaceNumberTypeCkIds,
        owning_repository_uuid,
    ):
        BnopObjects.__init__(
            self,
            uuid,
            owning_repository_uuid,
        )

        self.placing_type = placing_type

        self.placed_type = placed_type

        self.type_place_ckid = (
            type_place_ckid
        )
