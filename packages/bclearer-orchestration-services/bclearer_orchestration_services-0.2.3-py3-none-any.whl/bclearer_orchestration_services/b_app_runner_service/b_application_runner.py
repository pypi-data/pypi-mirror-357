from bclearer_orchestration_services.b_app_runner_service.app_startup_hard_crash_catch_wrapper_runner import (
    run_app_startup_hard_crash_catch_wrapper,
)
from bclearer_orchestration_services.b_app_runner_service.logging.application_logger_initialiser import (
    initialise_application_logger,
)


def run_b_application(
    app_startup_method, **kwargs
) -> None:
    initialise_application_logger()

    run_app_startup_hard_crash_catch_wrapper(
        app_startup_method=app_startup_method,
        **kwargs
    )
