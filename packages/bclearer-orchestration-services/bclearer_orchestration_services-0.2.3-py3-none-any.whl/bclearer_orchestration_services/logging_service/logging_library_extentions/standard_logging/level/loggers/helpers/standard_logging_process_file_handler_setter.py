import logging
import os

from bclearer_core.configurations.b_configurations.b_logging_configurations import (
    BLoggingConfigurations,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.formatters.standard_logging_process_flat_formatters import (
    StandardLoggingProcessFlatFormatters,
)
from bclearer_orchestration_services.reporting_service.reporters.log_file import (
    LogFiles,
)


def set_standard_logging_process_file_handler(
    standard_logging_process_logger,
):
    standard_logging_process_file_handler = (
        __get_standard_logging_process_file_handler()
    )

    standard_logging_process_logger.addHandler(
        standard_logging_process_file_handler
    )


def __get_standard_logging_process_file_handler():
    file_path = os.path.normpath(
        LogFiles.log_file.name
    )

    last_sep_index = file_path.rfind(
        os.path.sep
    )

    filepath_with_context = (
        os.path.join(
            file_path[:last_sep_index],
            "process_"
            + file_path[
                last_sep_index + 1 :
            ],
        )
    )

    file_handler = logging.FileHandler(
        filepath_with_context
    )

    file_handler.setLevel(
        level=BLoggingConfigurations.file_process_logging_level.value
    )

    formatter = StandardLoggingProcessFlatFormatters(
        "%(message)s"
    )

    file_handler.setFormatter(formatter)

    return file_handler
