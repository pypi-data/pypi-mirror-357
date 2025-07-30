from bclearer_core.ckids.boro_object_ckids import (
    BoroObjectCkIds,
)
from bnop.core.object_model.objects.bnop_objects import (
    BnopObjects,
)


class XmlBnopRegisters:
    __xml_model_branches = dict()

    __migrated_bnop_objects_keyed_by_ck_id = (
        dict()
    )

    @staticmethod
    def initialise_migration_uow():
        XmlBnopRegisters.__migrated_bnop_objects_keyed_by_ck_id = (
            BnopObjects.registry_keyed_on_ckid_type
        )

    @staticmethod
    def update_migration_uow(
        boro_ckid_type: BoroObjectCkIds,
        bnop_objects: list,
    ):
        XmlBnopRegisters.__migrated_bnop_objects_keyed_by_ck_id[
            boro_ckid_type
        ] = bnop_objects

    @staticmethod
    def get_migration_uow_type(
        boro_ckid_type: BoroObjectCkIds,
    ):
        return XmlBnopRegisters.__migrated_bnop_objects_keyed_by_ck_id[
            boro_ckid_type
        ]

    @staticmethod
    def clear_xml_model_branches():
        XmlBnopRegisters.__xml_model_branches.clear()

    @staticmethod
    def try_to_add_to_branches(
        bnop_object: BnopObjects,
        bnop_parent: BnopObjects,
    ) -> bool:
        success = True

        if (
            bnop_parent
            in XmlBnopRegisters.__xml_model_branches
        ):
            if (
                bnop_object
                in XmlBnopRegisters.__xml_model_branches[
                    bnop_parent
                ]
            ):
                return False

            else:
                XmlBnopRegisters.__xml_model_branches[
                    bnop_parent
                ].append(
                    bnop_object
                )

        else:
            success = XmlBnopRegisters.__try_to_add_to_trunks(
                bnop_object=bnop_object,
                bnop_parent=bnop_parent,
            )

        return success

    @staticmethod
    def __try_to_add_to_trunks(
        bnop_object: BnopObjects,
        bnop_parent: BnopObjects,
    ) -> bool:
        added_to_trunk = False

        for (
            branch_root,
            branch_trunk,
        ) in (
            XmlBnopRegisters.__xml_model_branches.items()
        ):
            added_to_trunk = XmlBnopRegisters.__try_to_add_to_trunk(
                bnop_object=bnop_object,
                bnop_parent=bnop_parent,
                branch_trunk=branch_trunk,
                branch_root=branch_root,
                added_to_trunk=added_to_trunk,
            )

        if not added_to_trunk:
            XmlBnopRegisters.__xml_model_branches[
                bnop_parent
            ] = [
                bnop_object
            ]

        return True

    @staticmethod
    def __try_to_add_to_trunk(
        bnop_object: BnopObjects,
        bnop_parent: BnopObjects,
        branch_trunk: list,
        branch_root: BnopObjects,
        added_to_trunk: bool,
    ) -> bool:
        if bnop_parent in branch_trunk:
            if (
                bnop_object
                in XmlBnopRegisters.__xml_model_branches[
                    branch_root
                ]
            ):
                return False

            else:
                XmlBnopRegisters.__xml_model_branches[
                    branch_root
                ].append(
                    bnop_object
                )

                added_to_trunk = True

        return added_to_trunk
