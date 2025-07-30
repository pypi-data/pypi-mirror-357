from enum import auto

from nf_common_base.b_source.configurations.datastructure.b_enums import (
    BEnums,
)


# TODO: Should this enum be moved to: core_graph_mvp_base/b_source/common_infrastructure/uncommon/cyto_utils ??
class CytoscapeNetworkInputColumnNames(
    BEnums
):
    NOT_SET = auto()

    ID = auto()

    SOURCE = auto()

    TARGET = auto()

    INTERACTION = auto()
