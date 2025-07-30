import os
import shutil

from nf_common_base.b_source.configurations.b_configurations.b_configurations import (
    BConfigurations,
)
from nf_common_base.b_source.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from nf_common_base.b_source.services.file_system_service.objects.files import (
    Files,
)
from nf_common_base.b_source.services.operating_system_services.is_platform_windows_checker import (
    check_is_platform_windows,
)
from nf_common_base.b_source.services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)


def delete_py4cytoscape_logs_handler() -> (
    None
):
    platform_is_windows = (
        check_is_platform_windows()
    )

    if not platform_is_windows:
        return

    py4cytoscape_log_file_path = (
        BConfigurations.APP_RUN_OUTPUT_FOLDER.absolute_path_string
        + os.sep
        + "logs"
        + os.sep
        + "py4cytoscape.log"
    )

    absolute_log_file_path = (
        os.path.abspath(
            py4cytoscape_log_file_path
        )
    )

    absolute_log_file = Files(
        absolute_path_string=absolute_log_file_path
    )

    if os.path.exists(
        absolute_log_file.absolute_path_string
    ):
        delete_folder_content(
            file_or_dir_path=absolute_log_file.absolute_path_string
        )

        delete_folder_content(
            file_or_dir_path=absolute_log_file.parent_absolute_path_string
        )


def delete_folder_content(
    file_or_dir_path: str,
) -> bool:
    try:
        if os.path.isfile(
            file_or_dir_path
        ):
            os.remove(file_or_dir_path)

        else:
            shutil.rmtree(
                file_or_dir_path,
                ignore_errors=True,
            )

        return True

    except OSError as e:
        log_inspection_message(
            message=f"Error deleting {file_or_dir_path}: {e}",
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.ERROR,
        )

        return False
