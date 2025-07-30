from bclearer_orchestration_services.logging_service.wrappers.logger_wrapper import (
    LoggerWrapper,
)


class LevelLoggerWrapper(LoggerWrapper):
    def __init__(self):
        super().__init__()
