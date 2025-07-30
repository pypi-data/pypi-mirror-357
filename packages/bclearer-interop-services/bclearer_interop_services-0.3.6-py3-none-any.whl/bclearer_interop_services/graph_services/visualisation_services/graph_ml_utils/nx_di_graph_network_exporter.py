import os

import networkx as nx
from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)


def export_nx_di_graph_network(
    level_n_full_network: nx.DiGraph,
    output_graphml_visualisations_folder: Folders,
    chosen_level: str,
):
    graphml_filename = (
        output_graphml_visualisations_folder.absolute_path_string
        + os.sep
        + chosen_level
        + "_nodes_hierarchy.graphml"
    )

    export_to_graphml(
        level_n_full_network,
        graphml_filename,
    )


def export_to_graphml(
    graph_nx: nx.DiGraph, filename: str
) -> None:
    nx.write_graphml(
        graph_nx,
        filename,
        encoding="utf-8",
        prettyprint=True,
    )
