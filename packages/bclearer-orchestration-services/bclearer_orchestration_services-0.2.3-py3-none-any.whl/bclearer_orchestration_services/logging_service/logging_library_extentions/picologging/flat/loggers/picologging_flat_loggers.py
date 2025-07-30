import os

import picologging
from nf_common_base.b_source.services.datetime_service.time_helpers.time_getter import (
    now_time_as_string,
)
from nf_common_base.b_source.services.log_environment_utility_service.common_knowledge.constants import (
    NAME_VALUE_DELIMITER,
)
from nf_common_base.b_source.services.reporting_service.reporters.log_file import (
    LogFiles,
)
from nf_common_base.b_source.services.reporting_service.reporters.nf_kafka_producers import (
    NfKafkaProducers,
)


class PicologgingFlatLoggers(
    picologging.Logger
):
    def __init__(self, name):
        super().__init__(name)

        handler = (
            picologging.StreamHandler()
        )

        formatter = picologging.Formatter(
            "%(name)s - %(levelname)s - %(message)s"
        )

        handler.setFormatter(formatter)

        self.addHandler(handler)

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
