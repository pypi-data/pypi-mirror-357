import logging
import os

from bclearer_orchestration_services.datetime_service.time_helpers.time_getter import (
    now_time_as_string,
)
from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import (
    NAME_VALUE_DELIMITER,
)
from bclearer_orchestration_services.reporting_service.reporters.log_file import (
    LogFiles,
)
from bclearer_orchestration_services.reporting_service.reporters.nf_kafka_producers import (
    NfKafkaProducers,
)


class StandardLoggingFlatLoggers(
    logging.Logger
):
    def __init__(self, name):
        super().__init__(name)
        console_handler = (
            logging.StreamHandler()
        )

        file_path = os.path.normpath(
            LogFiles.log_file.name
        )

        last_sep_index = (
            file_path.rfind(os.path.sep)
        )

        filepath_with_context = (
            os.path.join(
                file_path[
                    :last_sep_index
                ],
                "flat_"
                + file_path[
                    last_sep_index + 1 :
                ],
            )
        )

        file_handler = (
            logging.FileHandler(
                filepath_with_context
            )
        )

        console_handler.setLevel(
            level=logging.DEBUG
        )

        file_handler.setLevel(
            level=logging.DEBUG
        )

        formatter = logging.Formatter(
            "%(message)s"
        )

        console_handler.setFormatter(
            formatter
        )

        file_handler.setFormatter(
            formatter
        )

        self.addHandler(console_handler)
        self.addHandler(file_handler)

    @classmethod
    def log_flat(
        cls,
        message: str,
        is_headers: bool = False,
    ):
        date_stamped_message = message

        if not is_headers:
            date_stamped_message = (
                now_time_as_string()
                + NAME_VALUE_DELIMITER
                + message
            )

        print(date_stamped_message)

        LogFiles.write_to_log_file(
            message=date_stamped_message
            + os.linesep
        )

        NfKafkaProducers.log_to_kafka_producer(
            message=date_stamped_message
        )
