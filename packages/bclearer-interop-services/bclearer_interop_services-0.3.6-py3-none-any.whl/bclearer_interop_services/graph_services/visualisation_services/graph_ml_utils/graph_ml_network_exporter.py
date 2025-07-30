import networkx
from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.common.graph_report_bie_type_enums import (
    GraphReportBTypeEnums,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.common.output_visualisations_folder_getter import (
    get_output_visualisations_folder,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.graph_ml_utils.nx_di_graph_network_exporter import (
    export_nx_di_graph_network,
)


def export_graph_ml_network(
    b_clearer_run_root_folder: Folders,
    nx_di_graph_network: networkx.DiGraph,
    graph_report_bie_type_enum: GraphReportBTypeEnums,
) -> None:
    output_graphml_visualisations_folder = get_output_visualisations_folder(
        bclearer_run_root_folder=b_clearer_run_root_folder,
        grapy_type_folder_name="graphml",
    )

    export_nx_di_graph_network(
        level_n_full_network=nx_di_graph_network,
        output_graphml_visualisations_folder=output_graphml_visualisations_folder,
        chosen_level=graph_report_bie_type_enum.b_enum_item_name,
    )
