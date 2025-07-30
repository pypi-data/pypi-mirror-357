import os

from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)


def get_output_visualisations_folder(
    bclearer_run_root_folder: Folders,
    grapy_type_folder_name: str,
) -> Folders:
    output_visualisations_folder_path = os.path.join(
        bclearer_run_root_folder.absolute_path_string,
        "visualisations",
        grapy_type_folder_name,
    )

    os.makedirs(
        output_visualisations_folder_path,
        exist_ok=True,
    )

    output_visualisations_folder = Folders(
        absolute_path_string=output_visualisations_folder_path
    )

    return output_visualisations_folder
