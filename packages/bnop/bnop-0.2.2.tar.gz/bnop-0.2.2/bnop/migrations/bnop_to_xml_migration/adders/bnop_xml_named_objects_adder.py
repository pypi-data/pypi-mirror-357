from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.migrations.bnop_to_xml_migration.adders.bnop_object_xml_adder import (
    add_bnop_object_to_xml_tree,
)
from bnop.migrations.bnop_to_xml_migration.common_knowledge.bnop_to_xml_migration_configurations import (
    BnopToXmlMigrationConfigurations,
)
from bnop.migrations.bnop_to_xml_migration.xml_bnop_registers import (
    XmlBnopRegisters,
)
from lxml import etree
from lxml.etree import Element


def add_named_objects(
    xml_root: Element,
    configuration: BnopToXmlMigrationConfigurations,
):
    bnop_objects = XmlBnopRegisters.get_migration_uow_type(
        boro_ckid_type=BoroObjectCkIds.Objects
    )

    objects_tree_element = (
        etree.SubElement(
            xml_root, "Objects"
        )
    )

    for bnop_object in bnop_objects:
        if (
            len(
                bnop_object.is_named_bys
            )
            > 0
        ):
            add_bnop_object_to_xml_tree(
                bnop_object=bnop_object,
                parent_element=objects_tree_element,
                configuration=configuration,
            )
