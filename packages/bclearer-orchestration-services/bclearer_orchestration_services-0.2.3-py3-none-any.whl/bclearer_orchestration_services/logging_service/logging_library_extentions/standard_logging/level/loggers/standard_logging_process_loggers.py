import logging

from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.loggers.helpers.standard_logging_process_console_handler_setter import (
    set_standard_logging_process_console_handler,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.loggers.helpers.standard_logging_process_file_handler_setter import (
    set_standard_logging_process_file_handler,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.loggers.helpers.standard_logging_process_logging_levels_setter import (
    set_standard_logging_process_logging_levels,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.loggers.helpers.standard_logging_process_sqlite_handler_setter import (
    set_standard_logging_process_sqlite_handler,
)


class StandardLoggingProcessLoggers(
    logging.Logger
):
    def __init__(self, name):
        super().__init__(name)
        set_standard_logging_process_logging_levels(
            standard_logging_process_logger=self
        )

        set_standard_logging_process_console_handler(
            standard_logging_process_logger=self
        )

        set_standard_logging_process_file_handler(
            standard_logging_process_logger=self
        )

        set_standard_logging_process_sqlite_handler(
            standard_logging_process_logger=self
        )

    def debug(
        self, msg, *args, **kwargs
    ):
        pass

    def info(
        self, msg, *args, **kwargs
    ):
        pass

    def warning(
        self, msg, *args, **kwargs
    ):
        pass

    def error(
        self, msg, *args, **kwargs
    ):
        pass

    def critical(
        self, msg, *args, **kwargs
    ):
        pass
