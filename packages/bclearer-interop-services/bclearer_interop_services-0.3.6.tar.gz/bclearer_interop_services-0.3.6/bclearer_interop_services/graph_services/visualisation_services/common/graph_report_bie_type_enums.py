from enum import auto

from nf_common_base.b_source.configurations.datastructure.b_enums import (
    BEnums,
)


class GraphReportBTypeEnums(BEnums):
    NOT_SET = auto()

    DATASET_TRANSFORMATION_OVER_TIME_REPORT = (
        auto()
    )

    DATA_ITEM_TRANSFORMATION_OVER_TIME_REPORT = (
        auto()
    )

    DATA_TRANSFORMATION_OVER_TIME_REPORT_USING_PENDING_REGISTER = (
        auto()
    )

    DATA_TRANSFORMATION_OVER_TIME_REPORT = (
        auto()
    )

    DATA_TYPES_REPORT = auto()

    DATASET_TYPES_REPORT = auto()

    DATA_ITEM_TYPES_REPORT = auto()

    DATA_TYPES_WITH_COINCIDENCE_OVERLAPS_REPORT = (
        auto()
    )

    DATASET_TYPES_WITH_COINCIDENCE_OVERLAPS_REPORT = (
        auto()
    )

    DATA_ITEM_TYPES_WITH_COINCIDENCE_OVERLAPS_REPORT = (
        auto()
    )
