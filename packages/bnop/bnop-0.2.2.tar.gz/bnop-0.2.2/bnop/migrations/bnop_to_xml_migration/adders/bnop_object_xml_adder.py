from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)
from bnop.migrations.bnop_to_xml_migration.common_knowledge.bnop_to_xml_migration_configurations import (
    BnopToXmlMigrationConfigurations,
)
from lxml import etree
from lxml.etree import Element


def add_bnop_object_to_xml_tree(
    bnop_object: BnopObjects,
    parent_element: Element,
    configuration: BnopToXmlMigrationConfigurations,
):
    if (
        configuration.include_presentation_names
    ):
        object_tree_element = etree.SubElement(
            parent_element,
            BoroObjectCkIds.Objects.name,
            uuid=str(bnop_object.uuid),
            uml_name=bnop_object.uml_name,
        )

    else:
        object_tree_element = etree.SubElement(
            parent_element,
            BoroObjectCkIds.Objects.name,
            uuid=str(bnop_object.uuid),
        )

    add_bnop_object_types_to_xml_tree(
        bnop_object=bnop_object,
        object_tree_element=object_tree_element,
        configuration=configuration,
    )

    add_bnop_object_supertypes_to_xml_tree(
        bnop_object=bnop_object,
        object_tree_element=object_tree_element,
        configuration=configuration,
    )


def add_bnop_object_types_to_xml_tree(
    bnop_object: BnopObjects,
    object_tree_element: Element,
    configuration: BnopToXmlMigrationConfigurations,
):
    if len(bnop_object.types) == 0:
        return

    type_instances_tree_element = etree.SubElement(
        object_tree_element,
        BoroObjectCkIds.TypesInstances.name,
    )

    for bnop_type in bnop_object.types:
        if (
            configuration.include_presentation_names
        ):
            etree.SubElement(
                type_instances_tree_element,
                BoroObjectCkIds.Types.name,
                uuid=str(
                    bnop_type.uuid
                ),
                uml_name=bnop_type.uml_name,
            )

        else:
            etree.SubElement(
                type_instances_tree_element,
                BoroObjectCkIds.Types.name,
                uuid=str(
                    bnop_type.uuid
                ),
            )


def add_bnop_object_supertypes_to_xml_tree(
    bnop_object: BnopObjects,
    object_tree_element: Element,
    configuration: BnopToXmlMigrationConfigurations,
):
    if len(bnop_object.supertypes) == 0:
        return

    supertypes_tree_element = etree.SubElement(
        object_tree_element,
        BoroObjectCkIds.SuperSubTypes.name,
    )

    for (
        bnop_type
    ) in bnop_object.supertypes:
        if (
            configuration.include_presentation_names
        ):
            etree.SubElement(
                supertypes_tree_element,
                BoroObjectCkIds.Types.name,
                uuid=str(
                    bnop_type.uuid
                ),
                uml_name=bnop_type.uml_name,
            )

        else:
            etree.SubElement(
                supertypes_tree_element,
                BoroObjectCkIds.Types.name,
                uuid=str(
                    bnop_type.uuid
                ),
            )
