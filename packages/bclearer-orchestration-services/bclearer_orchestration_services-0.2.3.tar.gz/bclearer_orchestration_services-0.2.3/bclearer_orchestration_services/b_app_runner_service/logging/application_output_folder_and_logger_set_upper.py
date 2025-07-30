from bclearer_core.configurations.b_configurations.b_configurations import (
    BConfigurations,
)
from bclearer_interop_services.file_system_service.objects.folders_latest import (
    Folders,
)
from bclearer_orchestration_services.reporting_service.reporters.log_file import (
    LogFiles,
)


def set_up_application_output_folder_and_logger() -> (
    None
):
    app_run_output_file_system_folder = (
        __get_app_run_output_file_system_folder()
    )

    app_run_output_file_system_folder.make_me_on_disk()

    LogFiles.open_log_file(
        folder_path=app_run_output_file_system_folder.absolute_path
    )


def __get_app_run_output_file_system_folder() -> (
    Folders
):
    BConfigurations.set_up_app_run_output_folder_name()

    BConfigurations.set_app_run_output_folder()

    return (
        BConfigurations.APP_RUN_OUTPUT_FOLDER
    )
