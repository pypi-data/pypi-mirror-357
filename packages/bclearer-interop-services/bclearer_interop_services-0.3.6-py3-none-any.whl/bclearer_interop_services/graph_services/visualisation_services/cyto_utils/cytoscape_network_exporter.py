from nf_common_base.b_source.configurations.datastructure.b_enums import (
    BEnums,
)
from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.common.output_visualisations_folder_getter import (
    get_output_visualisations_folder,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.cytoscape_network_formater import (
    format_cytoscape_network,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.cytoscape_session_saver import (
    save_cytoscape_session,
)


def export_cytoscape_network(
    graph_report_bie_type_enum: BEnums,
    b_clearer_run_root_folder: Folders,
) -> None:
    # TODO: yFiles layouts are NOT available via CyREST, RCy3, nor py4cytoscape. Only use standard layouts.
    # TODO: create a new enum for all style types
    format_cytoscape_network(
        visual_style_name=graph_report_bie_type_enum.b_enum_item_name,
        layout_network_name="grid",
    )

    output_visualisations_cytoscape_folder = get_output_visualisations_folder(
        bclearer_run_root_folder=b_clearer_run_root_folder,
        grapy_type_folder_name="cytoscape",
    )

    save_cytoscape_session(
        output_visualisations_cytoscape_folder=output_visualisations_cytoscape_folder,
        filename_prefix=graph_report_bie_type_enum.b_enum_item_name,
    )
