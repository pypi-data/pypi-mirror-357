from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_tuples import (
    BnopTuples,
)


class BnopTupleFactories:

    @staticmethod
    def create(
        uuid,
        tuple_placed_objects_dictionary,
        immutable_minor_composition_couple_type_boro_object_ckid: BoroObjectCkIds,
        owning_repository_uuid,
    ):
        bnop_tuple = BnopTuples(
            uuid,
            tuple_placed_objects_dictionary,
            immutable_minor_composition_couple_type_boro_object_ckid,
            owning_repository_uuid,
        )

        return bnop_tuple
