from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.constants import *
from bclearer_orchestration_services.log_environment_utility_service.common_knowledge.log_function_header_enums import (
    LogFunctionHeaderEnums,
)
from bclearer_orchestration_services.reporting_service.reporters.log_with_datetime_latest import (
    log_message,
)


def log_run_and_log_function_all_header():
    column_names = [
        LogFunctionHeaderEnums.DATE_TIME.enum_header_name,
        LogFunctionHeaderEnums.LOGGING_TYPE.enum_header_name,
        LogFunctionHeaderEnums.STACK_LEVEL.enum_header_name,
        LogFunctionHeaderEnums.ACTION.enum_header_name,
        LogFunctionHeaderEnums.FUNCTION.enum_header_name,
        LogFunctionHeaderEnums.DISCRIMINATOR.enum_header_name,
        LogFunctionHeaderEnums.TOTAL_CPU_USAGE.enum_header_name,
        LogFunctionHeaderEnums.TOTAL_MEMORY.enum_header_name,
        LogFunctionHeaderEnums.AVAILABLE_MEMORY.enum_header_name,
        LogFunctionHeaderEnums.USED_MEMORY.enum_header_name,
        LogFunctionHeaderEnums.DURATION.enum_header_name,
    ]

    log_message(
        message=NAME_VALUE_DELIMITER.join(
            column_names
        ),
        is_headers=True,
    )
