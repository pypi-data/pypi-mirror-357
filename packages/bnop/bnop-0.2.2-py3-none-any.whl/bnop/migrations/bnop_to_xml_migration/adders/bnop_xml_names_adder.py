from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.migrations.bnop_to_xml_migration.adders.bnop_name_xml_adder import (
    add_bnop_name_to_xml_tree,
)
from bnop.migrations.bnop_to_xml_migration.common_knowledge.bnop_to_xml_migration_configurations import (
    BnopToXmlMigrationConfigurations,
)
from bnop.migrations.bnop_to_xml_migration.xml_bnop_registers import (
    XmlBnopRegisters,
)
from lxml import etree
from lxml.etree import Element


def add_names(
    xml_root: Element,
    configuration: BnopToXmlMigrationConfigurations,
):
    bnop_names = XmlBnopRegisters.get_migration_uow_type(
        boro_ckid_type=BoroObjectCkIds.Names
    )

    objects_tree_element = (
        etree.SubElement(
            xml_root, "Names"
        )
    )

    for bnop_name in bnop_names:
        add_bnop_name_to_xml_tree(
            bnop_name=bnop_name,
            parent_element=objects_tree_element,
            configuration=configuration,
        )
