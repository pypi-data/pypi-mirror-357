import py4cytoscape
from nf_common_base.b_source.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)


def check_cytoscape_app_is_running() -> (
    bool
):
    try:
        py4cytoscape.cytoscape_ping()

        return True

    except Exception as e:
        log_inspection_message(
            message="Cytoscape is not running. Please start Cytoscape and try again.",
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.VERBOSE,
        )

        return False
