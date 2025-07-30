from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_representations import (
    BnopRepresentations,
)


class BnopNames(BnopRepresentations):
    def __init__(
        self,
        uuid,
        exemplar_representation,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        BnopRepresentations.__init__(
            self,
            uuid,
            exemplar_representation,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        self.naming_spaces = set()

        self.add_to_registry_keyed_on_ckid_type(
            BoroObjectCkIds.Names
        )
