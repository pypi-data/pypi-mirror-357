from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)


class BnopObjects(object):
    registry_keyed_on_uuid = {}

    registry_keyed_on_ckid_type = {}

    matched_objects = []

    def __init__(
        self,
        uuid,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        self.uuid = uuid

        self.registry_keyed_on_uuid.update(
            {self.uuid: self}
        )

        self.owning_repository_uuid = (
            owning_repository_uuid
        )

        self.is_named_bys = set()

        self.names = set()

        self.types = set()

        self.instances = set()

        self.supertypes = set()

        self.subtypes = set()

        self.uml_name = (
            presentation_name
        )

        self.naming_spaces = set()

    def add_to_registry_keyed_on_ckid_type(
        self,
        boro_object_ck_id: BoroObjectCkIds,
    ):

        if (
            boro_object_ck_id
            in self.registry_keyed_on_ckid_type
        ):
            ckid_typed_objects = self.registry_keyed_on_ckid_type[
                boro_object_ck_id
            ]
        else:
            ckid_typed_objects = set()

            self.registry_keyed_on_ckid_type.update(
                {
                    boro_object_ck_id: ckid_typed_objects
                }
            )

        ckid_typed_objects.add(self)

    @staticmethod
    def import_bnop_object(bnop_object):
        BnopObjects.registry_keyed_on_uuid.update(
            {
                bnop_object.uuid: bnop_object
            }
        )

        return bnop_object

    @staticmethod
    def add_to_matched_objects(
        bnop_object,
    ):
        BnopObjects.matched_objects.append(
            bnop_object.uuid
        )
