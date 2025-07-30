from bnop.core.object_model.objects.bnop_elements import (
    BnopElements,
)


class BnopElementFactories:

    @staticmethod
    def create(
        uuid, owning_repository_uuid
    ):
        bnop_element = BnopElements(
            uuid, owning_repository_uuid
        )

        return bnop_element
