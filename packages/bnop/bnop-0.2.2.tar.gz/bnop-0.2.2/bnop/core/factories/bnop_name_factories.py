from bnop.core.object_model.objects.bnop_names import (
    BnopNames,
)


class BnopNameFactories:

    @staticmethod
    def create(
        uuid,
        exemplar_representation,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        bnop_name = BnopNames(
            uuid,
            exemplar_representation,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        return bnop_name
