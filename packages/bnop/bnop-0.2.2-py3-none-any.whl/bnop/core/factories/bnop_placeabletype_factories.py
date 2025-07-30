from bnop.core.object_model.objects.bnop_placeable_types import (
    BnopPlaceableTypes,
)


class BnopPlaceableTypeFactories:

    @staticmethod
    def create(
        uuid,
        placeable_type_placed_types_dictionary,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        bnop_placeabletype = BnopPlaceableTypes(
            uuid,
            placeable_type_placed_types_dictionary,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        return bnop_placeabletype
