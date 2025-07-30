import time

from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import (
    OVERALL_RUN,
)
from bclearer_orchestration_services.logging_service.configuration.process_logging_levels import (
    ProcessLoggingLevels,
)
from bclearer_orchestration_services.logging_service.wrappers.flat_logger_wrapper import (
    FlatLoggerWrapper,
)
from bclearer_orchestration_services.logging_service.wrappers.process_logger_wrapper import (
    ProcessLoggerWrapper,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.process_finish_logger import (
    log_process_finish,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.process_message_standard_dictionary_getter import (
    get_process_message_standard_dictionary,
)
from bclearer_orchestration_services.reporting_service.reporters.log_file import (
    LogFiles,
)


def end_run_logging(
    run_start_time: time,
    process_logging_level: ProcessLoggingLevels = ProcessLoggingLevels.PROCESS_LEVEL_NOT_GIVEN,
) -> None:
    process_message_standard_dictionary = get_process_message_standard_dictionary(
        function_name=OVERALL_RUN,
        function_discriminator_name=str(),
    )

    log_process_finish(
        process_start_log_time=run_start_time,
        process_message_standard_dictionary=process_message_standard_dictionary,
        process_logging_level=process_logging_level,
    )

    ProcessLoggerWrapper.close()

    FlatLoggerWrapper.close()

    LogFiles.close_log_file()
