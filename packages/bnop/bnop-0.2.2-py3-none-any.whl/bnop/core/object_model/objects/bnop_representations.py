from bnop.core.object_model.objects.bnop_types import (
    BnopTypes,
)


class BnopRepresentations(BnopTypes):

    def __init__(
        self,
        uuid,
        exemplar_representation,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        BnopTypes.__init__(
            self,
            uuid,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        self.exemplar_representation = (
            exemplar_representation
        )
