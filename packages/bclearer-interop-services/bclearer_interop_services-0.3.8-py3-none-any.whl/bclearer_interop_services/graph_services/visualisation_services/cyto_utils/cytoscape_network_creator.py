import os

import networkx as nx
import py4cytoscape
from nf_common_base.b_source.configurations.datastructure.b_enums import (
    BEnums,
)
from nf_common_base.b_source.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from nf_common_base.b_source.services.file_system_service.objects.files import (
    Files,
)
from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.helpers.cytoscape_network_legend_generator import (
    generate_cytoscape_network_legend,
)
from promote_to_nf_common_base.resources.cytoscape.file_system_folder_for_cytoscape_getter import (
    get_file_system_folder_for_cytoscape_folder,
)


def create_cytoscape_network(
    level_n_full_network: nx.DiGraph,
    graph_report_bie_type_enum: BEnums,
    collection_name: str,
) -> None:
    for x in level_n_full_network.nodes:
        pass

    py4cytoscape.create_network_from_networkx(
        level_n_full_network,
        title=graph_report_bie_type_enum.b_enum_item_name,
        collection=collection_name,
    )

    # TODO: network has to be created previously
    py4cytoscape.toggle_graphics_details()

    data_transformation_style_xml_file = __set_up_cytoscape_styles(
        graph_report_bie_type_enum=graph_report_bie_type_enum
    )

    generate_cytoscape_network_legend(
        data_transformation_style_xml_file=data_transformation_style_xml_file
    )


# TODO: the style is general for all nested graphs in cyto. cannot use multiple at the same time - to research -
#  it has to be move some levels down
def __set_up_cytoscape_styles(
    graph_report_bie_type_enum: BEnums,
) -> Files:
    data_transformation_style_xml_path = get_file_system_folder_for_cytoscape_folder().extend_path(
        graph_report_bie_type_enum.b_enum_item_name.replace(
            "_report", "_style"
        )
        + ".xml"
    )

    data_transformation_style_xml_file = Files(
        absolute_path=data_transformation_style_xml_path
    )

    if not os.path.exists(
        data_transformation_style_xml_file.absolute_path_string
    ):
        return None

    py4cytoscape.import_visual_styles(
        filename=data_transformation_style_xml_file.absolute_path_string
    )

    style_all_mappings = py4cytoscape.get_style_all_mappings(
        style_name=graph_report_bie_type_enum.b_enum_item_name
    )

    if not style_all_mappings:
        log_inspection_message(
            message="Style could not be load.",
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.INFO,
        )

    return data_transformation_style_xml_file
