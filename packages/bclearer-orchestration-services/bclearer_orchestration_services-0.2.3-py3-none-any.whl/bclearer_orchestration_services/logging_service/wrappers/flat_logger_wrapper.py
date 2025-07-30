from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.flat_logger_facade import (
    FlatLoggerFacade,
)
from bclearer_orchestration_services.logging_service.wrappers.logger_wrapper import (
    LoggerWrapper,
)


class FlatLoggerWrapper(LoggerWrapper):
    def __init__(self):
        super().__init__()

    @staticmethod
    def log(
        message: str,
        is_headers: bool = False,
    ) -> None:
        FlatLoggerFacade.log(
            message=message,
            is_headers=is_headers,
        )

    @staticmethod
    def close():
        FlatLoggerFacade.close()
