from bclearer_core.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from bclearer_orchestration_services.b_app_runner_service.logging.run_logging_ender import (
    end_run_logging,
)
from bclearer_orchestration_services.b_app_runner_service.logging.run_logging_starter import (
    start_run_logging,
)
from bclearer_orchestration_services.reporting_service.reporters.inspection_message_logger import (
    log_inspection_message,
)


def run_app_startup_hard_crash_catch_wrapper(
    app_startup_method, **kwargs
) -> None:
    # TODO: Logging: add start_run_logging - think about a common start time - DONE
    run_start_time = start_run_logging()

    try:
        app_startup_method(**kwargs)

        end_run_logging(
            run_start_time=run_start_time
        )

    except Exception as error:
        error_message_name = (
            type(error).__name__
            + " occurred when running app"
        )

        log_inspection_message(
            message=error_message_name,
            logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.CRITICAL,
        )

        if str(error):
            error_message_description = "Error message:" + str(
                error
            )

            log_inspection_message(
                message=error_message_description,
                logging_inspection_level_b_enum=LoggingInspectionLevelBEnums.CRITICAL,
            )

        end_run_logging(
            run_start_time=run_start_time
        )

        exit(1)
