import logging
import os

from nf_common_base.b_source.configurations.b_configurations.b_configurations import (
    BConfigurations,
)
from nf_common_base.b_source.services.reporting_service.reporters.log_file import (
    LogFiles,
)


def update_py4cytoscape_logs_handler() -> (
    None
):
    log_file_path = (
        BConfigurations.APP_RUN_OUTPUT_FOLDER.absolute_path_string
        + os.sep
        + "py4cytoscape.log"
    )

    os.environ[
        "PY4CYTOSCAPE_CONFIG_DIR"
    ] = str(LogFiles.folder_path)

    os.environ[
        "PY4CYTOSCAPE_DETAIL_LOGGER_DIR"
    ] = str(LogFiles.folder_path)

    logging.basicConfig(
        filename=log_file_path,
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s:%(message)s",
    )

    py4cytoscape_logger = (
        logging.getLogger(
            "py4cytoscape"
        )
    )

    for (
        handler
    ) in py4cytoscape_logger.handlers[
        :
    ]:
        py4cytoscape_logger.removeHandler(
            hdlr=handler
        )

    file_handler = logging.FileHandler(
        log_file_path
    )

    file_handler.setLevel(logging.DEBUG)

    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s:%(message)s"
        )
    )

    py4cytoscape_logger.addHandler(
        file_handler
    )

    py4cytoscape_logger.setLevel(
        logging.DEBUG
    )
