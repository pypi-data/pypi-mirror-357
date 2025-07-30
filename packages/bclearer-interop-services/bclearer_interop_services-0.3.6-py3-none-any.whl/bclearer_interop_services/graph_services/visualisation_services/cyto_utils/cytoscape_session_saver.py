import os
import shutil

import py4cytoscape
from nf_common_base.b_source.services.datetime_service.time_helpers.time_getter import (
    now_time_as_string_for_files,
)
from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)


def save_cytoscape_session(
    output_visualisations_cytoscape_folder: Folders,
    filename_prefix: str,
) -> None:
    cytoscape_session_file_path = os.path.join(
        output_visualisations_cytoscape_folder.absolute_path_string,
        filename_prefix
        + "_network_"
        + now_time_as_string_for_files()
        + ".cys",
    )

    temporary_cytoscape_session_file_path = os.path.expanduser(
        "~/Documents/temporary_cytoscape_session.cys"
    )

    py4cytoscape.save_session(
        temporary_cytoscape_session_file_path
    )

    shutil.move(
        temporary_cytoscape_session_file_path,
        cytoscape_session_file_path,
    )

    py4cytoscape.close_session(
        save_before_closing=True
    )
