from nf_common_base.b_source.services.logging_service.wrappers.level_logger_wrapper import (
    LevelLoggerWrapper,
)


class EventLoggerWrapper(
    LevelLoggerWrapper
):
    def __init__(self):
        super().__init__()
