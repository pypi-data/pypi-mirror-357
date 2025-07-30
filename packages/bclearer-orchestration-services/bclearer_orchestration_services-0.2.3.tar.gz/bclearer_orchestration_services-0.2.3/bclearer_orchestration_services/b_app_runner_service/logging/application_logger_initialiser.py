from bclearer_orchestration_services.b_app_runner_service.logging.application_output_folder_and_logger_set_upper import (
    set_up_application_output_folder_and_logger,
)
from bclearer_orchestration_services.b_app_runner_service.logging.logger_initialiser import (
    log_initial_logs,
)


def initialise_application_logger() -> (
    None
):
    set_up_application_output_folder_and_logger()

    log_initial_logs()
