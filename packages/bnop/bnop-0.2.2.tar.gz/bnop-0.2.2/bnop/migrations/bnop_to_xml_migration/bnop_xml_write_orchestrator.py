from bnop.migrations.bnop_to_xml_migration.common_knowledge.vanilla_bnop_to_xml_migration_configurations import (
    VanillaBnopToXmlMigrationConfigurations,
)
from bnop.migrations.bnop_to_xml_migration.xml_bnop_registers import (
    XmlBnopRegisters,
)
from lxml import etree


def orchestrate_xml_write(
    xml_file_path: str,
    configuration=VanillaBnopToXmlMigrationConfigurations(),
):
    root_element = etree.Element(
        "Model"
    )

    XmlBnopRegisters.initialise_migration_uow()

    for (
        bnop_sorter
    ) in (
        configuration.bnop_object_sorters
    ):
        bnop_sorter()

    for (
        section_creator
    ) in (
        configuration.xml_section_creators
    ):
        section_creator(
            root_element, configuration
        )

    tree = etree.ElementTree(
        element=root_element
    )

    tree.write(
        xml_file_path, pretty_print=True
    )
