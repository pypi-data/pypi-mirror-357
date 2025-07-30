from bclearer_orchestration_services.datetime_service.time_helpers.time_getter import (
    now_time_as_string,
)
from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import (
    NAME_VALUE_DELIMITER,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.flat.loggers.standard_logging_flat_loggers import (
    StandardLoggingFlatLoggers,
)
from bclearer_orchestration_services.reporting_service.reporters.log_file import (
    LogFiles,
)


class FlatLoggerFacade:
    __logger = None

    @classmethod
    def log(
        cls,
        message: str,
        is_headers: bool = False,
    ) -> None:
        date_stamped_message = (
            now_time_as_string()
            + NAME_VALUE_DELIMITER
            + message
        )

        if not cls.__logger:
            if not LogFiles.log_file:
                print(
                    date_stamped_message,
                    ": CONSOLE ONLY - NO LOGGER SET",
                )

                return

            cls.__logger = StandardLoggingFlatLoggers(
                "standard_logging_flat_logger"
            )

        cls.__logger.debug(
            msg=date_stamped_message
        )

    @classmethod
    def close(cls):
        cls.__logger = None
