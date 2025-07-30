from pandas import DataFrame
from promote_to_nf_common_base.b_sevices.visualisation_services.common.cytoscape_network_input_column_names import (
    CytoscapeNetworkInputColumnNames,
)


class NetworkXGraphResources:
    def __init__(
        self,
        edges_dataset: DataFrame,
        nodes_dataset: DataFrame,
        edge_attribute_column_name: str,
    ):
        self.edges_dataset = (
            edges_dataset
        )

        self.nodes_dataset = (
            nodes_dataset
        )

        self.node_identity_column_name = (
            CytoscapeNetworkInputColumnNames.ID.b_enum_item_name
        )

        self.edge_source_column_name = (
            CytoscapeNetworkInputColumnNames.SOURCE.b_enum_item_name
        )

        self.edge_target_column_name = (
            CytoscapeNetworkInputColumnNames.TARGET.b_enum_item_name
        )

        self.edge_attribute_column_name = (
            edge_attribute_column_name
        )
