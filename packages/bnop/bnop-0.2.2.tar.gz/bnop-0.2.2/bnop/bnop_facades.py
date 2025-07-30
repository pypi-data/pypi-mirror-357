from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bclearer_core.ckids.place_number_type_ckids import (
    PlaceNumberTypeCkIds,
)
from bclearer_orchestration_services.identification_services.uuid_service.uuid_helpers.uuid_factory import (
    create_new_uuid,
)
from bnop.core.factories.bnop_element_factories import (
    BnopElementFactories,
)
from bnop.core.factories.bnop_name_factories import (
    BnopNameFactories,
)
from bnop.core.factories.bnop_object_factories import (
    BnopObjectFactories,
)
from bnop.core.factories.bnop_placeabletype_factories import (
    BnopPlaceableTypeFactories,
)
from bnop.core.factories.bnop_tuple_factories import (
    BnopTupleFactories,
)
from bnop.core.factories.bnop_type_factories import (
    BnopTypeFactories,
)
from bnop.core.factories.bnop_type_place_factories import (
    BnopTypePlaceFactories,
)
from bnop.core.object_model.objects.bnop_names import (
    BnopNames,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)
from bnop.core.object_model.objects.places.bnop_placed_objects_dictionaries import (
    BnopPlacedObjectsDictionaries,
)
from bnop.core.object_model.objects.places.bnop_placed_types_dictionaries import (
    BnopPlacedTypesDictionaries,
)
from bnop.migrations.bnop_to_xml_migration.bnop_xml_write_orchestrator import (
    orchestrate_xml_write,
)


class BnopFacades:

    @staticmethod
    def write_bnop_object_to_xml(
        xml_file_path: str,
    ):
        orchestrate_xml_write(
            xml_file_path=xml_file_path
        )

    @staticmethod
    def create_new_bnop_type(
        owning_repository_uuid,
    ):
        bnop_type = (
            BnopTypeFactories.create(
                create_new_uuid(),
                owning_repository_uuid,
            )
        )

        return bnop_type

    @staticmethod
    def create_bnop_object(
        object_uuid,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        bnop_object = BnopObjectFactories.create(
            object_uuid,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        return bnop_object

    @staticmethod
    def create_bnop_type(
        type_uuid,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        bnop_type = BnopTypeFactories.create(
            type_uuid,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        return bnop_type

    @staticmethod
    def create_new_bnop_element(
        owning_repository_uuid,
    ):
        bnop_element = (
            BnopElementFactories.create(
                create_new_uuid(),
                owning_repository_uuid,
            )
        )

        return bnop_element

    @staticmethod
    def create_bnop_element(
        element_uuid,
        owning_repository_uuid,
    ):
        bnop_element = (
            BnopElementFactories.create(
                element_uuid,
                owning_repository_uuid,
            )
        )

        return bnop_element

    @staticmethod
    def create_new_bnop_name(
        exemplar_representation,
        owning_repository_uuid,
    ):
        bnop_name = (
            BnopNameFactories.create(
                create_new_uuid(),
                exemplar_representation,
                owning_repository_uuid,
            )
        )

        return bnop_name

    @staticmethod
    def create_bnop_name(
        name_uuid,
        exemplar_representation,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        bnop_name = BnopNameFactories.create(
            name_uuid,
            exemplar_representation,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        return bnop_name

    @staticmethod
    def create_new_bnop_tuple_from_two_placed_objects(
        placed1_object,
        placed2_object,
        immutable_minor_composition_couple_type_boro_object_ckid,
        owning_repository_uuid,
    ):
        tuple_placed_objects_dictionary = (
            BnopPlacedObjectsDictionaries()
        )

        tuple_placed_objects_dictionary.add_tuple_placed_object_to_dictionary(
            PlaceNumberTypeCkIds.PlaceNumberOnes,
            placed1_object,
        )

        tuple_placed_objects_dictionary.add_tuple_placed_object_to_dictionary(
            PlaceNumberTypeCkIds.PlaceNumberTwos,
            placed2_object,
        )

        bnop_tuple = BnopTupleFactories.create(
            create_new_uuid(),
            tuple_placed_objects_dictionary,
            immutable_minor_composition_couple_type_boro_object_ckid,
            owning_repository_uuid,
        )

        return bnop_tuple

    @staticmethod
    def create_bnop_tuple_from_two_placed_objects(
        tuple_uuid,
        placed1_object: BnopObjects,
        placed2_object: BnopObjects,
        immutable_minor_composition_couple_type_boro_object_ckid: BoroObjectCkIds,
        owning_repository_uuid,
    ):
        tuple_placed_objects_dictionary = (
            BnopPlacedObjectsDictionaries()
        )

        tuple_placed_objects_dictionary.add_tuple_placed_object_to_dictionary(
            PlaceNumberTypeCkIds.PlaceNumberOnes,
            placed1_object,
        )

        tuple_placed_objects_dictionary.add_tuple_placed_object_to_dictionary(
            PlaceNumberTypeCkIds.PlaceNumberTwos,
            placed2_object,
        )

        bnop_tuple = BnopTupleFactories.create(
            tuple_uuid,
            tuple_placed_objects_dictionary,
            immutable_minor_composition_couple_type_boro_object_ckid,
            owning_repository_uuid,
        )

        if (
            immutable_minor_composition_couple_type_boro_object_ckid
            == BoroObjectCkIds.SuperSubTypes
        ):
            placed2_object.supertypes.add(
                placed1_object
            )

            placed1_object.subtypes.add(
                placed2_object
            )

        if (
            immutable_minor_composition_couple_type_boro_object_ckid
            == BoroObjectCkIds.NamedBy
        ):
            placed1_object.is_named_bys.add(
                placed2_object
            )

            placed2_object.names.add(
                placed1_object
            )

        if (
            immutable_minor_composition_couple_type_boro_object_ckid
            == BoroObjectCkIds.TypesInstances
        ):
            placed2_object.types.add(
                placed1_object
            )

            placed1_object.instances.add(
                placed2_object
            )

            if (
                type(placed2_object)
                is BnopNames
            ):
                placed2_object.naming_spaces.add(
                    placed1_object
                )

        return bnop_tuple

    @staticmethod
    def create_bnop_placeabletype(
        placeabletype_uuid,
        owning_repository_uuid,
        presentation_name=str(),
    ):
        placeable_type_placed_type_dictionary = (
            BnopPlacedTypesDictionaries()
        )

        bnop_placeabletype = BnopPlaceableTypeFactories.create(
            placeabletype_uuid,
            placeable_type_placed_type_dictionary,
            owning_repository_uuid,
            presentation_name=presentation_name,
        )

        return bnop_placeabletype

    @staticmethod
    def create_bnop_type_place(
        type_place_uuid,
        placing_type,
        placed_type,
        type_place_ckid,
        owning_repository_uuid,
    ):
        bnop_type_place = BnopTypePlaceFactories.create(
            type_place_uuid,
            placing_type,
            placed_type,
            type_place_ckid,
            owning_repository_uuid,
        )

        return bnop_type_place

    @staticmethod
    def __add_placed_type_to_placeabletype(
        placed_type,
        place_number_ckid,
        placeable_type,
    ):
        placeable_type.placeable_type_placed_types_dictionary[
            place_number_ckid
        ] = placed_type
