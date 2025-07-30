import logging

from bclearer_core.configurations.b_configurations.b_logging_configurations import (
    BLoggingConfigurations,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.formatters.standard_logging_process_flat_formatters import (
    StandardLoggingProcessFlatFormatters,
)


def set_standard_logging_process_console_handler(
    standard_logging_process_logger,
):
    standard_logging_process_console_handler = (
        __get_standard_logging_process_console_handler()
    )

    standard_logging_process_logger.addHandler(
        standard_logging_process_console_handler
    )


def __get_standard_logging_process_console_handler():
    console_handler = (
        logging.StreamHandler()
    )

    console_handler.setLevel(
        level=BLoggingConfigurations.console_process_logging_level.value
    )

    formatter = StandardLoggingProcessFlatFormatters(
        "%(message)s"
    )

    console_handler.setFormatter(
        formatter
    )

    return console_handler
