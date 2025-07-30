from collections import OrderedDict

from bclearer_orchestration_services.datetime_service.time_helpers.time_getter import (
    now_time_as_string,
)
from bclearer_orchestration_services.logging_service.logging_library_extentions.standard_logging.level.loggers.standard_logging_process_loggers import (
    StandardLoggingProcessLoggers,
)
from bclearer_orchestration_services.reporting_service.reporters.log_file import (
    LogFiles,
)


class ProcessLoggerFacade:
    __logger = None

    @classmethod
    def log(
        cls,
        process_message_standard_dictionary: dict,
        process_logging_level: int,
    ) -> None:
        timed_process_message_standard_ordered_dictionary = OrderedDict(
            list(
                {
                    "logged": now_time_as_string()
                }.items()
            )
            + list(
                process_message_standard_dictionary.items()
            )
        )

        timed_process_message_standard_dictionary = dict(
            timed_process_message_standard_ordered_dictionary
        )

        if not cls.__logger:
            if not LogFiles.log_file:
                print(
                    timed_process_message_standard_dictionary,
                    ": CONSOLE ONLY - NO LOGGER SET",
                )

                return

            cls.__logger = StandardLoggingProcessLoggers(
                "standard_logging_process_logger"
            )

        cls.__logger.log(
            msg=timed_process_message_standard_dictionary,
            level=process_logging_level,
        )

    @classmethod
    def close(cls):
        cls.__logger = None
