from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.bnop_facades import (
    BnopFacades,
)
from bnop.core.object_model.objects.bnop_names import (
    BnopNames,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)
from bnop.core.object_model.objects.bnop_types import (
    BnopTypes,
)


def add_name_if_required(
    named_object: BnopObjects,
    name: BnopNames,
    naming_space: BnopTypes,
    owning_repository_uuid,
):
    BnopFacades.create_new_bnop_tuple_from_two_placed_objects(
        naming_space,
        name,
        BoroObjectCkIds.TypesInstances,
        owning_repository_uuid,
    )

    BnopFacades.create_new_bnop_tuple_from_two_placed_objects(
        named_object,
        name,
        BoroObjectCkIds.NamedBy,
        owning_repository_uuid,
    )


def add_exemplar_name_if_required(
    named_object: BnopObjects,
    exemplar_name: str,
    naming_space: BnopTypes,
    owning_repository_uuid,
):
    name = BnopFacades.create_new_bnop_name(
        exemplar_name,
        owning_repository_uuid,
    )

    add_name_if_required(
        named_object,
        name,
        naming_space,
        owning_repository_uuid,
    )
