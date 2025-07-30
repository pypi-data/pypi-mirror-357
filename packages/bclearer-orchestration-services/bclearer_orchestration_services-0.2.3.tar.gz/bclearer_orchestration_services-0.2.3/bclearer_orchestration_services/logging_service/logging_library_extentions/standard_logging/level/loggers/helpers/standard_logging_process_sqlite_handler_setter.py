import logging
import os

from bclearer_core.configurations.b_configurations.b_logging_configurations import (
    BLoggingConfigurations,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.handlers.standard_logging_process_sqlite_handlers import (
    StandardLoggingProcessSQLiteHandlers,
)
from bclearer_orchestration_services.reporting_service.reporters.log_file import (
    LogFiles,
)


def set_standard_logging_process_sqlite_handler(
    standard_logging_process_logger,
):
    standard_logging_process_sqlite_handler = (
        __get_standard_logging_process_sqlite_handler()
    )

    standard_logging_process_logger.addHandler(
        standard_logging_process_sqlite_handler
    )


def __get_standard_logging_process_sqlite_handler():
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
                last_sep_index + 1 : -3
            ]
            + "db",
        )
    )

    sqlite_handler = StandardLoggingProcessSQLiteHandlers(
        db_path=filepath_with_context
    )

    sqlite_handler.setLevel(
        level=BLoggingConfigurations.console_process_logging_level.value
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    sqlite_handler.setFormatter(
        formatter
    )

    return sqlite_handler
