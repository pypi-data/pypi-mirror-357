from bclearer_core.configurations.b_configurations.b_logging_configurations import (
    BLoggingConfigurations,
)
from bclearer_core.configurations.datastructure.logging_inspection_level_b_enums import (
    LoggingInspectionLevelBEnums,
)
from bclearer_orchestration_services.reporting_service.reporters.helpers.log_message_reporter import (
    report_log_message,
)


def log_inspection_message(
    message: str,
    logging_inspection_level_b_enum: LoggingInspectionLevelBEnums,
) -> None:
    is_message_to_be_logged = __is_message_to_be_logged(
        logging_inspection_level_b_enum=logging_inspection_level_b_enum
    )

    if not is_message_to_be_logged:
        return

    date_stamped_message = report_log_message(
        message=message,
        logging_inspection_level_b_enum=logging_inspection_level_b_enum,
    )

    is_message_to_be_summarised = __is_message_to_be_summarised(
        logging_inspection_level_b_enum=logging_inspection_level_b_enum
    )

    if not is_message_to_be_summarised:
        return

    __summarise_message(
        date_stamped_message=date_stamped_message
    )


def __is_message_to_be_logged(
    logging_inspection_level_b_enum: LoggingInspectionLevelBEnums,
) -> bool:
    current_logging_inspection_level_enum = (
        BLoggingConfigurations.LOGGING_INSPECTION_REPORTING_LEVEL_ENUM
    )

    is_message_to_be_logged = (
        logging_inspection_level_b_enum.enum_level_weight
        >= current_logging_inspection_level_enum.enum_level_weight
    )

    return is_message_to_be_logged


def __is_message_to_be_summarised(
    logging_inspection_level_b_enum: LoggingInspectionLevelBEnums,
) -> bool:
    current_logging_summarising_level_enum = (
        BLoggingConfigurations.LOGGING_INSPECTION_SUMMARISING_LEVEL_ENUM
    )

    is_message_to_be_summarised = (
        logging_inspection_level_b_enum.enum_level_weight
        >= current_logging_summarising_level_enum.enum_level_weight
    )

    return is_message_to_be_summarised


def __summarise_message(
    date_stamped_message: str,
) -> None:
    # TODO: CPa-logging to be done - see ANTLR
    pass
