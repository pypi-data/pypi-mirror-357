import psutil
from bclearer_orchestration_services.reporting_service.reporters.helpers.stack_level_getter import (
    get_stack_level,
)


def get_process_message_standard_dictionary(
    function_name: str,
    function_discriminator_name: str,
) -> dict:
    # TODO: replace NAME_VALUE_DELIMITER to STACK_LEVEL
    stack_level = get_stack_level()

    total_cpu_usage = (
        f"{psutil.cpu_percent()}%"
    )

    system_virtual_memory = (
        psutil.virtual_memory()
    )

    total_memory = f"{__get_gigabytes(byte_count=system_virtual_memory.total):.2f}"

    available_memory = f"{__get_gigabytes(byte_count=system_virtual_memory.available):.2f}"

    used_memory = f"{__get_gigabytes(byte_count=system_virtual_memory.used):.2f}"

    process_message_standard_dictionary = {
        "stack_level": stack_level,
        "function_name": function_name,
        "function_discriminator_name": function_discriminator_name,
        "total_cpu_usage": total_cpu_usage,
        "total_memory": total_memory,
        "available_memory": available_memory,
        "used_memory": used_memory,
    }

    return process_message_standard_dictionary


def __get_gigabytes(
    byte_count: int,
) -> float:
    gigabytes = (
        byte_count / 1024 / 1024 / 1024
    )

    return gigabytes
