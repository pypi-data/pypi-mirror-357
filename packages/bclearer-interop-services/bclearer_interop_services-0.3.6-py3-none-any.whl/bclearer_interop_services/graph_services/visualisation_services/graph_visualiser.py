import matplotlib.pyplot as plt
import networkx as nx


def visualize_graph(graph):
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(graph)

    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_color="skyblue",
        node_size=1500,
        font_size=10,
    )

    edge_labels = (
        nx.get_edge_attributes(
            graph, "relation"
        )
    )
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
    )

    plt.title("Knowledge Graph")
    plt.tight_layout()
    plt.show()
