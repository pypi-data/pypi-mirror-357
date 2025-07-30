from bnop.core.object_model.objects.bnop_type_places import (
    BnopTypePlaces,
)


class BnopTypePlaceFactories:

    @staticmethod
    def create(
        uuid,
        placing_type,
        placed_type,
        type_place_ckid,
        owning_repository_uuid,
    ):
        bnop_type_place = (
            BnopTypePlaces(
                uuid,
                placing_type,
                placed_type,
                type_place_ckid,
                owning_repository_uuid,
            )
        )

        return bnop_type_place
