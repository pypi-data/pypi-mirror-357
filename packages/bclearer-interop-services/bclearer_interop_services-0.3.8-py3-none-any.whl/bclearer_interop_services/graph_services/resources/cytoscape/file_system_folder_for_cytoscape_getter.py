from pathlib import Path

from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)


def get_file_system_folder_for_cytoscape_folder() -> (
    Folders
):
    file_system_folder_for_cytoscape_folder = Folders(
        absolute_path=Path(
            __file__
        ).parent
    )

    return file_system_folder_for_cytoscape_folder
