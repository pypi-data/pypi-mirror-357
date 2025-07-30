import os
import subprocess

from nf_common_base.b_source.configurations.b_graph_configurations.bie_cytoscape_inspection_configurations import (
    BieCytoscapeInspectionConfigurations,
)
from nf_common_base.b_source.services.b_app_runner_service.logging.run_logging_starter import (
    start_run_logging,
)
from nf_common_base.b_source.services.operating_system_services.is_platform_windows_checker import (
    check_is_platform_windows,
)
from promote_to_nf_common_base.b_sevices.visualisation_services.cyto_utils.helpers.cytoscape_installation_folder_getter import (
    get_cytoscape_installation_folder,
)


def start_cytoscape() -> float:
    start_time = start_run_logging()

    os.environ["JAVA_TOOL_OPTIONS"] = (
        f"-Xmx{BieCytoscapeInspectionConfigurations.CYTOSCAPE_MAXIMUM_ALLOCATED_RAM_MEMORY}G"
    )

    cytoscape_installation_folder = (
        get_cytoscape_installation_folder()
    )

    platform_is_windows = (
        check_is_platform_windows()
    )

    if platform_is_windows:
        __linux_start_cytoscape(
            cytoscape_path=cytoscape_installation_folder.absolute_path_string
        )

    else:
        __macos_start_cytoscape(
            cytoscape_path=cytoscape_installation_folder.absolute_path_string
        )

    return start_time


def __macos_start_cytoscape(
    cytoscape_path: str,
) -> None:
    if cytoscape_path:
        subprocess.run(
            [
                "open",
                "-a",
                cytoscape_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )


def __linux_start_cytoscape(
    cytoscape_path: str,
) -> None:
    if cytoscape_path:
        subprocess.Popen(
            [cytoscape_path]
        )
