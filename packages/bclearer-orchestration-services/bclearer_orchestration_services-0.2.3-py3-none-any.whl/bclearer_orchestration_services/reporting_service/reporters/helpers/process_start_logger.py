from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import (
    LOG_START,
)
from bclearer_orchestration_services.logging_service.configuration.process_logging_levels import (
    ProcessLoggingLevels,
)
from bclearer_orchestration_services.logging_service.wrappers.process_logger_wrapper import (
    ProcessLoggerWrapper,
)


def log_process_start(
    process_message_standard_dictionary: dict,
    process_logging_level: ProcessLoggingLevels = ProcessLoggingLevels.PROCESS_LEVEL_NOT_GIVEN,
) -> None:
    process_message_standard_dictionary[
        "event"
    ] = LOG_START

    ProcessLoggerWrapper.log(
        process_message_standard_dictionary=process_message_standard_dictionary,
        process_logging_level=process_logging_level,
    )
