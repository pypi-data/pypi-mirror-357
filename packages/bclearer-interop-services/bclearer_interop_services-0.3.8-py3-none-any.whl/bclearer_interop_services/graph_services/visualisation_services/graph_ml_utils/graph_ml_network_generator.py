import networkx
from promote_to_nf_common_base.b_sevices.visualisation_services.common.network_x_graph_resources import (
    NetworkXGraphResources,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.graph_ml_utils.nx_di_graph_network_creator import (
    create_nx_di_graph_network,
)


# TODO: getting the networkx DiGraph and exporting the networkx DiGraph as graphML are two different things. Split this
#  function accordingly. - DONE
def generate_graph_ml_network(
    network_x_graph_resources_instance: NetworkXGraphResources,
) -> networkx.DiGraph:
    nx_di_graph_network = create_nx_di_graph_network(
        network_x_graph_resources_instance
    )

    return nx_di_graph_network
