import logging

import py4cytoscape
from nf_common_base.b_source.configurations.b_graph_configurations.bie_cytoscape_inspection_configurations import (
    BieCytoscapeInspectionConfigurations,
)
from nf_common_base.b_source.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)


def set_cytoscape_is_running_configuration() -> (
    None
):
    try:
        logging.getLogger(
            "py4cytoscape"
        ).setLevel(logging.ERROR)

        py4cytoscape.cytoscape_system.cytoscape_ping()

        BieCytoscapeInspectionConfigurations.CYTOSCAPE_IS_RUNNING = (
            True
        )

    # TODO: add a catch - to check global errors - DONE
    except Exception as error:
        log_inspection_message(
            message=str(error),
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.ERROR,
        )

        BieCytoscapeInspectionConfigurations.CYTOSCAPE_IS_RUNNING = (
            False
        )
