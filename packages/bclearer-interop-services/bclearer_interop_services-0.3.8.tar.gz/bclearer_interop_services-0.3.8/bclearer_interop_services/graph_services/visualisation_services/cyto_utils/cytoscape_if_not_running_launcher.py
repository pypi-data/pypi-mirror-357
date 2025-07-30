import time

from nf_common_base.b_source.configurations.b_graph_configurations.bie_cytoscape_inspection_configurations import (
    BieCytoscapeInspectionConfigurations,
)
from nf_common_base.b_source.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)
from nf_common_base.b_source.services.reporting_service.wrappers.run_and_log_function_wrapper import (
    run_and_log_function,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.cytoscape_starter import (
    start_cytoscape,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.helpers.cytoscape_is_running_configuration_setter import (
    set_cytoscape_is_running_configuration,
)


@run_and_log_function()
def launch_cytoscape_if_not_running() -> (
    None
):
    set_cytoscape_is_running_configuration()

    if (
        BieCytoscapeInspectionConfigurations.CYTOSCAPE_IS_RUNNING
    ):
        return

    start_time = start_cytoscape()

    max_wait_time = (
        BieCytoscapeInspectionConfigurations.CYTOSCAPE_WAIT_TIME
    )

    wait_interval = round(
        BieCytoscapeInspectionConfigurations.CYTOSCAPE_WAIT_TIME
        / BieCytoscapeInspectionConfigurations.CYTOSCAPE_NUMBER_OF_WAIT_INTERVALS
    )

    elapsed_time = 0

    __check_cytoscape_status(
        wait_interval=wait_interval,
        elapsed_time=elapsed_time,
        max_wait_time=max_wait_time,
    )

    execution_time = round(
        time.time()
        - (start_time + elapsed_time),
        0,
    )

    log_inspection_message(
        message="Time spent waiting to execute Cytoscape: {0} seconds.".format(
            execution_time
        ),
        logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.INFO,
    )


def __check_cytoscape_status(
    wait_interval: float,
    elapsed_time: float,
    max_wait_time: float,
):
    while elapsed_time < max_wait_time:
        set_cytoscape_is_running_configuration()

        if (
            BieCytoscapeInspectionConfigurations.CYTOSCAPE_IS_RUNNING
        ):
            break

        time.sleep(wait_interval)

        elapsed_time += wait_interval
