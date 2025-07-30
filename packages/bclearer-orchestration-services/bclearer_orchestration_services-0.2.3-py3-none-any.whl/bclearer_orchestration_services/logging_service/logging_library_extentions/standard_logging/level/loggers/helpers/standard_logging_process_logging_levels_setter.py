import logging

from bclearer_orchestration_services.logging_service.configuration.process_logging_levels import (
    ProcessLoggingLevels,
)


def set_standard_logging_process_logging_levels(
    standard_logging_process_logger,
):
    for (
        process_logging_level
    ) in ProcessLoggingLevels:
        __set_process_logging_level(
            standard_logging_process_logger=standard_logging_process_logger,
            process_logging_level=process_logging_level,
        )


def __set_process_logging_level(
    standard_logging_process_logger,
    process_logging_level: ProcessLoggingLevels,
):
    process_logging_level_name = (
        process_logging_level.name
    )

    process_logging_level_value = (
        process_logging_level.value
    )

    logging.addLevelName(
        process_logging_level_value,
        process_logging_level_name,
    )

    def log_for_level(
        message, *args, **kwargs
    ):
        if standard_logging_process_logger.isEnabledFor(
            process_logging_level_value
        ):
            standard_logging_process_logger._log(
                process_logging_level_value,
                message,
                args,
                **kwargs
            )

    setattr(
        standard_logging_process_logger,
        process_logging_level_name.lower(),
        log_for_level,
    )
