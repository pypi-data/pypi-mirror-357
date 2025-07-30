from bclearer_orchestration_services.logging_service.configuration.process_logging_levels import (
    ProcessLoggingLevels,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.process_logger_facade import (
    ProcessLoggerFacade,
)
from bclearer_orchestration_services.logging_service.wrappers.level_logger_wrapper import (
    LevelLoggerWrapper,
)


class ProcessLoggerWrapper(
    LevelLoggerWrapper
):
    def __init__(self):
        super().__init__()

    @staticmethod
    def log(
        process_message_standard_dictionary: dict,
        process_logging_level: ProcessLoggingLevels = ProcessLoggingLevels.PROCESS_LEVEL_NOT_GIVEN,
    ) -> None:
        ProcessLoggerFacade.log(
            process_message_standard_dictionary=process_message_standard_dictionary,
            process_logging_level=process_logging_level.value,
        )

    @staticmethod
    def close():
        ProcessLoggerFacade.close()
