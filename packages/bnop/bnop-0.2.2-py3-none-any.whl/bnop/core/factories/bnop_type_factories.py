from bnop.core.factories.bnop_object_factories import (
    BnopObjectFactories,
)
from bnop.core.object_model.objects.bnop_types import (
    BnopTypes,
)


class BnopTypeFactories(
    BnopObjectFactories
):
    pass

    @staticmethod
    def create(
        uuid,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        bnop_type = BnopTypes(
            uuid,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        return bnop_type
