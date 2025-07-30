import xml.etree.ElementTree as ElementTree


def get_populated_legend_info_dictionary(
    root: ElementTree.Element,
) -> dict:
    legend_info = dict()

    parent_child_pairs = []

    def process_element(
        element, parent=None
    ):
        if (
            element.tag
            == "discreteMapping"
        ):
            if parent is not None:
                parent_child_pairs.append(
                    (parent, element)
                )

        for child in element:
            process_element(
                element=child,
                parent=element,
            )

    process_element(element=root)

    for (
        parent_child_tuple
    ) in parent_child_pairs:
        parent_tag = parent_child_tuple[
            0
        ]

        discrete_mapping_tag = (
            parent_child_tuple[1]
        )

        attribute_name = (
            discrete_mapping_tag.attrib[
                "attributeName"
            ]
        )

        legend_info[attribute_name] = (
            __get_legend_individual_entries(
                discrete_mapping_tag=discrete_mapping_tag,
                parent_tag=parent_tag,
            )
        )

    return legend_info


def __get_legend_individual_entries(
    discrete_mapping_tag: ElementTree.Element,
    parent_tag: ElementTree.Element,
) -> list:
    entries = list()

    for (
        entry
    ) in discrete_mapping_tag.findall(
        ".//discreteMappingEntry"
    ):
        attribute_value = entry.attrib[
            "attributeValue"
        ]

        value = entry.attrib["value"]

        parent_tag_name = (
            parent_tag.attrib["name"]
        )

        pretty_parent_tag_name = __get_pretty_parent_tag_name(
            parent_tag_name=parent_tag_name
        )

        entries.append(
            (
                pretty_parent_tag_name,
                attribute_value,
                value,
            )
        )

    return entries


def __get_pretty_parent_tag_name(
    parent_tag_name: str,
) -> str:
    if (
        parent_tag_name
        == "NODE_FILL_COLOR"
    ):
        return "Node Fill Color"

    if parent_tag_name == "NODE_SHAPE":
        return "Node Shape"

    if (
        parent_tag_name
        == "EDGE_STROKE_UNSELECTED_PAINT"
    ):
        return "Edges Fill Color"

    if parent_tag_name == "NODE_WIDTH":
        return "Node Width"

    if (
        parent_tag_name
        == "EDGE_LINE_TYPE"
    ):
        return "Edge Line Type"

    return parent_tag_name
