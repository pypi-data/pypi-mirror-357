import subprocess

from nf_common_base.b_source.services.file_system_service.objects.folders import (
    Folders,
)
from nf_common_base.b_source.services.operating_system_services.is_platform_windows_checker import (
    check_is_platform_windows,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.cyto_literals import (
    MY_CYTOSCAPE_MAC_SYSTEM_PATH,
    MY_CYTOSCAPE_WINDOWS_SYSTEM_PATH,
)


def get_cytoscape_installation_folder() -> (
    Folders
):
    try:
        platform_is_windows = (
            check_is_platform_windows()
        )

        if platform_is_windows:
            command = 'for /d %i in ("C:\\Program Files\\*") do @echo %~nxi'

            command_results = (
                subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                )
            )

            installation_folder_path = __get_installation_folder_path(
                command_results=command_results,
                my_cytoscape_os_based_system_path=MY_CYTOSCAPE_WINDOWS_SYSTEM_PATH,
            )

            installation_folder = Folders(
                absolute_path_string=installation_folder_path
            )

        else:
            command_results = (
                subprocess.run(
                    [
                        "ls",
                        "/Applications",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            )

            installation_folder_path = __get_installation_folder_path(
                command_results=command_results,
                my_cytoscape_os_based_system_path=MY_CYTOSCAPE_MAC_SYSTEM_PATH,
            )

            installation_folder = Folders(
                absolute_path_string=installation_folder_path
            )

        return installation_folder

    except (
        subprocess.CalledProcessError
    ):
        raise FileNotFoundError(
            "Cytoscape executable not found."
        )


def __get_installation_folder_path(
    command_results: subprocess.CompletedProcess[
        str
    ],
    my_cytoscape_os_based_system_path: str,
) -> str:
    app_names = (
        command_results.stdout.strip().splitlines()
    )

    installation_folder_name = next(
        (
            app_name
            for app_name in app_names
            if "Cytoscape_v" in app_name
        ),
        None,
    )

    installation_folder_path = my_cytoscape_os_based_system_path.replace(
        "<installation_folder_version>",
        installation_folder_name,
    )

    return installation_folder_path
