import xml.etree.ElementTree as ElementTree

import py4cytoscape
from nf_common_base.b_source.services.file_system_service.objects.files import (
    Files,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.helpers.populated_legend_info_dictionary_getter import (
    get_populated_legend_info_dictionary,
)


def generate_cytoscape_network_legend(
    data_transformation_style_xml_file: Files,
) -> None:
    if (
        not data_transformation_style_xml_file.absolute_path_string
    ):
        return

    tree = ElementTree.parse(
        source=data_transformation_style_xml_file.absolute_path_string
    )

    root = tree.getroot()

    __add_general_section_to_legend(
        root=root
    )


def __add_general_section_to_legend(
    root,
):
    legend_info = get_populated_legend_info_dictionary(
        root=root
    )

    # TODO: DZa - hardcoded values, to fix.
    y_position = 250

    vertical_spacing = 25

    __add_main_sections_to_legend(
        legend_info=legend_info,
        y_position=y_position,
        vertical_spacing=vertical_spacing,
    )


def __add_main_sections_to_legend(
    legend_info,
    y_position: int,
    vertical_spacing: int,
) -> None:
    for (
        attribute_name,
        entries,
    ) in legend_info.items():
        py4cytoscape.add_annotation_text(
            text=entries[0][0]
            + ": "
            + attribute_name,
            y_pos=y_position,
            font_size=14,
            font_style="bold",
        )

        y_position += vertical_spacing

        y_position = __add_specific_item_to_general_section(
            entries=entries,
            y_position=y_position,
            vertical_spacing=vertical_spacing,
        )

        y_position += 10


def __add_specific_item_to_general_section(
    entries: list,
    y_position: int,
    vertical_spacing: int,
) -> int:
    for (
        parent_tag_name,
        attribute_value,
        value,
    ) in entries:
        color = None

        if value.startswith("#"):
            color = value

        label = attribute_value

        custom_shape = "ROUND_RECTANGLE"

        if not color:
            if (
                value
                not in py4cytoscape.get_node_shapes()
            ):
                custom_shape = None

                label = (
                    label
                    + ": "
                    + str(value)
                )

            else:
                custom_shape = value

        py4cytoscape.add_annotation_shape(
            type=custom_shape,
            y_pos=y_position,
            width=20,
            height=20,
            fill_color=color,
            border_color=color,
        )

        py4cytoscape.add_annotation_text(
            text=label,
            x_pos=30,
            y_pos=y_position + 10,
            font_size=12,
        )

        y_position += vertical_spacing

    return y_position
