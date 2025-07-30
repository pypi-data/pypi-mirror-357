import py4cytoscape
from nf_common_base.b_source.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)


def format_cytoscape_network(
    visual_style_name: str,
    layout_network_name: str,
) -> None:
    __apply_style_hard_crash_wrapper(
        visual_style_name=visual_style_name
    )

    py4cytoscape.layout_network(
        layout_network_name
    )


def __apply_style_hard_crash_wrapper(
    visual_style_name: str,
):
    try:
        py4cytoscape.set_visual_style(
            visual_style_name
        )

    except Exception as error:
        log_inspection_message(
            message="Error occurred trying to apply style:{0} - Error: {1}".format(
                visual_style_name,
                str(error),
            ),
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.ERROR,
        )
