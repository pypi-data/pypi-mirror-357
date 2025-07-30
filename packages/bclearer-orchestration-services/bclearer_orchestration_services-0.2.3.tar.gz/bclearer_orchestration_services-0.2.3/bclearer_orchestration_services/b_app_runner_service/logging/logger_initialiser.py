from bclearer_core.configurations.b_configurations.run_environment_logging_configurations import (
    RunEnvironmentLoggingConfigurations,
)
from bclearer_interop_services.file_system_service.objects.folders import (
    Folders,
)
from bclearer_orchestration_services.b_app_runner_service.logging.output_folder_and_logger_set_upper import (
    set_up_output_folder_and_logger,
)
from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.environment_log_level_types import (
    EnvironmentLogLevelTypes,
)
from bclearer_orchestration_services.log_environment_utility_service.loggers.environment_logger import (
    log_filtered_environment,
    log_full_environment,
)
from bclearer_orchestration_services.reporting_service.wrappers.run_and_log_function_all_header_logger import (
    log_run_and_log_function_all_header,
)


def initialise_logger(
    output_folder_prefix: str,
    output_folder_suffix: str,
    output_root_folder: Folders,
) -> None:
    __set_up_logger(
        output_folder_prefix=output_folder_prefix,
        output_folder_suffix=output_folder_suffix,
        output_root_folder=output_root_folder,
    )

    log_initial_logs()


def __set_up_logger(
    output_folder_prefix: str,
    output_folder_suffix: str,
    output_root_folder: Folders,
) -> None:
    set_up_output_folder_and_logger(
        output_root_folder=output_root_folder,
        output_folder_prefix=output_folder_prefix,
        output_folder_suffix=output_folder_suffix,
    )


def log_initial_logs() -> None:
    log_run_and_log_function_all_header()

    # TODO: first attempt to move it failed: partially initialized module
    match RunEnvironmentLoggingConfigurations.ENVIRONMENT_LOG_LEVEL_TYPE:
        case (
            EnvironmentLogLevelTypes.FILTERED
        ):
            log_filtered_environment()

        case (
            EnvironmentLogLevelTypes.FULL
        ):
            log_full_environment()

        case (
            EnvironmentLogLevelTypes.NONE
        ):
            pass
