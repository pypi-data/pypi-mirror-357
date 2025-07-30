import time

from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import (
    OVERALL_RUN,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.process_message_standard_dictionary_getter import (
    get_process_message_standard_dictionary,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.process_start_logger import (
    log_process_start,
)


def start_run_logging() -> float:
    process_message_standard_dictionary = get_process_message_standard_dictionary(
        function_name=OVERALL_RUN,
        function_discriminator_name=str(),
    )

    log_process_start(
        process_message_standard_dictionary=process_message_standard_dictionary
    )

    run_start_time = time.time()

    return run_start_time
