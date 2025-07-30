import time

from bclearer_core.configurations.b_configurations.b_logging_configurations import (
    BLoggingConfigurations,
)
from bclearer_orchestration_services.logging_service.configuration.process_logging_levels import (
    ProcessLoggingLevels,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.process_finish_logger import (
    log_process_finish,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.process_message_standard_dictionary_getter import (
    get_process_message_standard_dictionary,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.process_start_logger import (
    log_process_start,
)


def run_and_log_function(
    process_logging_level=ProcessLoggingLevels.PROCESS_LEVEL_NOT_GIVEN,
):
    def decorator(function):
        def timed(*args, **kwargs):
            if (
                not BLoggingConfigurations.LOG_PROCESS_MESSAGES_FLAG
            ):
                return

            process_start_log_time = (
                time.time()
            )

            process_message_standard_dictionary = __get_process_message_standard_dictionary(
                kwargs, function
            )

            log_process_start(
                process_message_standard_dictionary=process_message_standard_dictionary,
                process_logging_level=process_logging_level,
            )

            return_value = function(
                *args, **kwargs
            )

            log_process_finish(
                process_start_log_time=process_start_log_time,
                process_message_standard_dictionary=process_message_standard_dictionary,
                process_logging_level=process_logging_level,
            )

            return return_value

        return timed

    return decorator


def __get_process_message_standard_dictionary(
    kwargs, function
) -> dict:
    function_discriminator_name = kwargs.pop(
        "function_discriminator_name",
        str(),
    )

    function_name = function.__name__

    function_discriminator_name = str(
        function_discriminator_name
    )

    process_message_standard_dictionary = get_process_message_standard_dictionary(
        function_name=function_name,
        function_discriminator_name=function_discriminator_name,
    )

    return process_message_standard_dictionary
