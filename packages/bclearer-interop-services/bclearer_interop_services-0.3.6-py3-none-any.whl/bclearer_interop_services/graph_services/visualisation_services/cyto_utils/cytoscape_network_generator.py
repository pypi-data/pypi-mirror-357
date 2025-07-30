import networkx as networkx
from nf_common_base.b_source.configurations.datastructure.b_enums import (
    BEnums,
)
from nf_common_base.b_source.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)
from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.cytoscape_network_creator import (
    create_cytoscape_network,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.cytoscape_network_exporter import (
    export_cytoscape_network,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.helpers.cytoscape_app_is_running_checker import (
    check_cytoscape_app_is_running,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.helpers.py4cytoscape_logs_handler_updater import (
    update_py4cytoscape_logs_handler,
)


def generate_cytoscape_network(
    nx_di_graph_network: networkx.DiGraph,
    graph_report_bie_type_enum: BEnums,
    b_clearer_run_root_folder: Folders,
    collection_name: str,
) -> None:
    update_py4cytoscape_logs_handler()

    # TODO: if not, report a message and don't initiate it because it should be open somewhere else - DONE
    if (
        not check_cytoscape_app_is_running()
    ):
        log_inspection_message(
            message="Cyto is not currently running.",
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.WARNING,
        )

        return

    create_cytoscape_network(
        level_n_full_network=nx_di_graph_network,
        graph_report_bie_type_enum=graph_report_bie_type_enum,
        collection_name=collection_name,
    )

    export_cytoscape_network(
        graph_report_bie_type_enum=graph_report_bie_type_enum,
        b_clearer_run_root_folder=b_clearer_run_root_folder,
    )
