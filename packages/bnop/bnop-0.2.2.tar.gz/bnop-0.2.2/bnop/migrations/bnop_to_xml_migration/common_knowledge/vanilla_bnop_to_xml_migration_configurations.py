from bnop.migrations.bnop_to_xml_migration.adders.bnop_xml_named_objects_adder import (
    add_named_objects,
)
from bnop.migrations.bnop_to_xml_migration.adders.bnop_xml_names_adder import (
    add_names,
)
from bnop.migrations.bnop_to_xml_migration.common_knowledge.bnop_to_xml_migration_configurations import (
    BnopToXmlMigrationConfigurations,
)
from bnop.migrations.bnop_to_xml_migration.sorters.bnop_name_sorters import (
    sort_names_by_named_objects,
)


class VanillaBnopToXmlMigrationConfigurations(
    BnopToXmlMigrationConfigurations
):
    include_presentation_names = False

    xml_section_creators = [
        add_named_objects,
        add_names,
    ]

    bnop_object_sorters = [
        sort_names_by_named_objects
    ]
