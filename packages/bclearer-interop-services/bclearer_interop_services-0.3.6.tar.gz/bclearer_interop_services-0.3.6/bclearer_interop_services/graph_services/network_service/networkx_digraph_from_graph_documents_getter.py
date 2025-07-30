from typing import List

from bclearer_orchestration_services.reporting_service.wrappers.run_and_log_function_wrapper_latest import (
    run_and_log_function,
)
from langchain_community.graphs.graph_document import (
    GraphDocument,
)
from networkx.algorithms.operators.binary import (
    compose,
)
from networkx.classes import DiGraph


# TODO: move this to a graph_rag services or data_export/interop
@run_and_log_function()
def get_networkx_digraph_from_graph_documents(
    graph_documents: List[
        GraphDocument
    ],
) -> DiGraph:
    combined_graph = DiGraph()

    for (
        graph_document
    ) in graph_documents:
        combined_graph = __add_graph_document_graph_to_combined_graph(
            combined_graph=combined_graph,
            graph_document=graph_document,
        )

    return combined_graph


def __add_graph_document_graph_to_combined_graph(
    combined_graph: DiGraph,
    graph_document: GraphDocument,
) -> DiGraph:
    networkx_digraph = DiGraph()

    nodes = getattr(
        graph_document, "nodes", []
    )

    edges = getattr(
        graph_document,
        "relationships",
        [],
    )

    for node in nodes:
        networkx_digraph.add_node(
            node_for_adding=f"{node.id}",
            type=node.type,
        )

    for edge in edges:
        __add_edge_components_to_graph_document_graph(
            edge=edge,
            networkx_digraph=networkx_digraph,
        )

    combined_graph = compose(
        combined_graph, networkx_digraph
    )

    return combined_graph


def __add_edge_components_to_graph_document_graph(
    edge, networkx_digraph: DiGraph
) -> None:
    source = f"{edge.source.id}"

    target = f"{edge.target.id}"

    networkx_digraph.add_edge(
        source, target, type=edge.type
    )
