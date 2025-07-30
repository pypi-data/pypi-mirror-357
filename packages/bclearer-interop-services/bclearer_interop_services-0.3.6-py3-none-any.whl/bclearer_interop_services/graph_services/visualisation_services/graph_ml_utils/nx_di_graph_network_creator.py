import networkx
from promote_to_nf_common_base.b_sevices.visualisation_services.common.network_x_graph_resources import (
    NetworkXGraphResources,
)


def create_nx_di_graph_network(
    network_x_graph_resources_instance: NetworkXGraphResources,
) -> networkx.DiGraph:
    edges_dataset = network_x_graph_resources_instance.edges_dataset.astype(
        str
    )

    nodes_dataset = network_x_graph_resources_instance.nodes_dataset.astype(
        str
    )

    nx_di_graph_network = networkx.from_pandas_edgelist(
        edges_dataset,
        source=network_x_graph_resources_instance.edge_source_column_name,
        target=network_x_graph_resources_instance.edge_target_column_name,
        edge_attr=network_x_graph_resources_instance.edge_attribute_column_name,
        create_using=networkx.DiGraph,
    )

    for (
        index,
        row,
    ) in nodes_dataset.iterrows():
        # TODO: parameters are flexible keep the same name in the report: bie_type_names and bie_instance_names
        nx_di_graph_network.add_node(
            row[
                network_x_graph_resources_instance.node_identity_column_name
            ],
            bie_type_names=row[
                "bie_type_names"
            ],
            bie_instance_names=row[
                "bie_instance_names"
            ],
            parent_data_types=row[
                "parent_data_types"
            ],
        )

    return nx_di_graph_network
