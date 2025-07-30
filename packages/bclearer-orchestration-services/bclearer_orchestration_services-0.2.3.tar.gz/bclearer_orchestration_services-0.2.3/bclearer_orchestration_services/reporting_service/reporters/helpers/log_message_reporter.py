from bclearer_core.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import (
    INSPECTION_PREFIX,
    NAME_VALUE_DELIMITER,
)
from bclearer_orchestration_services.reporting_service.reporters.log_with_datetime import (
    log_message,
)


def report_log_message(
    message: str,
    logging_inspection_level_b_enum: LoggingInspectionLevelBEnums,
) -> str:
    date_stamped_message = NAME_VALUE_DELIMITER.join(
        [
            INSPECTION_PREFIX,
            logging_inspection_level_b_enum.name,
            message,
        ]
    )

    log_message(
        message=date_stamped_message
    )

    return date_stamped_message
