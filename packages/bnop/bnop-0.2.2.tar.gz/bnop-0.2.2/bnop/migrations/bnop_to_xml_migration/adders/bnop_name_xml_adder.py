from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_names import (
    BnopNames,
)
from bnop.migrations.bnop_to_xml_migration.adders.bnop_object_xml_adder import (
    add_bnop_object_types_to_xml_tree,
)
from bnop.migrations.bnop_to_xml_migration.common_knowledge.bnop_to_xml_migration_configurations import (
    BnopToXmlMigrationConfigurations,
)
from lxml import etree
from lxml.etree import Element


def add_bnop_name_to_xml_tree(
    bnop_name: BnopNames,
    parent_element: Element,
    configuration: BnopToXmlMigrationConfigurations,
):
    if (
        configuration.include_presentation_names
    ):
        name_tree_element = etree.SubElement(
            parent_element,
            BoroObjectCkIds.Names.name,
            uuid=str(bnop_name.uuid),
            uml_name=bnop_name.uml_name,
            name_exemplar=bnop_name.exemplar_representation,
        )

    else:
        name_tree_element = etree.SubElement(
            parent_element,
            BoroObjectCkIds.Names.name,
            uuid=str(bnop_name.uuid),
            name_exemplar=bnop_name.exemplar_representation,
        )

    __add_bnop_named_by_objects_to_xml_tree(
        bnop_name=bnop_name,
        name_tree_element=name_tree_element,
        configuration=configuration,
    )

    add_bnop_object_types_to_xml_tree(
        bnop_object=bnop_name,
        object_tree_element=name_tree_element,
        configuration=configuration,
    )


def __add_bnop_named_by_objects_to_xml_tree(
    bnop_name: BnopNames,
    name_tree_element: Element,
    configuration: BnopToXmlMigrationConfigurations,
):
    if len(bnop_name.names) == 0:
        return

    named_by_tree_element = etree.SubElement(
        name_tree_element,
        BoroObjectCkIds.NamedBy.name,
    )

    for (
        bnop_named_object
    ) in bnop_name.names:
        if (
            configuration.include_presentation_names
        ):
            etree.SubElement(
                named_by_tree_element,
                BoroObjectCkIds.Objects.name,
                uuid=str(
                    bnop_named_object.uuid
                ),
                uml_name=bnop_named_object.uml_name,
            )

        else:
            etree.SubElement(
                named_by_tree_element,
                BoroObjectCkIds.Objects.name,
                uuid=str(
                    bnop_named_object.uuid
                ),
            )
