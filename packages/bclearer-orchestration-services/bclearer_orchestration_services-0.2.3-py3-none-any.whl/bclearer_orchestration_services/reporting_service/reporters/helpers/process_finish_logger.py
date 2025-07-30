import time

from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import (
    LOG_END,
)
from bclearer_orchestration_services.logging_service.configuration.process_logging_levels import (
    ProcessLoggingLevels,
)
from bclearer_orchestration_services.logging_service.wrappers.process_logger_wrapper import (
    ProcessLoggerWrapper,
)


def log_process_finish(
    process_start_log_time: time,
    process_message_standard_dictionary: dict,
    process_logging_level: ProcessLoggingLevels = ProcessLoggingLevels.PROCESS_LEVEL_NOT_GIVEN,
) -> None:
    process_message_standard_dictionary[
        "event"
    ] = LOG_END

    process_end_log_time = time.time()

    duration = f"{process_end_log_time - process_start_log_time:.2f}"

    process_message_standard_dictionary[
        "duration"
    ] = duration

    ProcessLoggerWrapper.log(
        process_message_standard_dictionary=process_message_standard_dictionary,
        process_logging_level=process_logging_level,
    )
