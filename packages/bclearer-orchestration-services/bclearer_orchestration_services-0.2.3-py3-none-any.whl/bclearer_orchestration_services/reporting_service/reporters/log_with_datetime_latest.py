from bclearer_orchestration_services.logging_service.wrappers.flat_logger_wrapper import (
    FlatLoggerWrapper,
)


# TODO: Note that the (process) log_inspection_message via report_log_message uses this?
def log_message(
    message: str,
    is_headers: bool = False,
):
    # TODO: NEW LOGGING: replace lines 17 to 31 with line 14
    FlatLoggerWrapper.log(
        message=message,
        is_headers=is_headers,
    )
