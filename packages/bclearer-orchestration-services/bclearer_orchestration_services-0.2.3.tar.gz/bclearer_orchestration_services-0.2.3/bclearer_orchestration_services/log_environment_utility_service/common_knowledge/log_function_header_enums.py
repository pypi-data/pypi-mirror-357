from enum import Enum, auto


class LogFunctionHeaderEnums(Enum):
    NOT_SET = auto()

    DATE_TIME = auto()

    LOGGING_TYPE = auto()

    STACK_LEVEL = auto()

    ACTION = auto()

    FUNCTION = auto()

    DISCRIMINATOR = auto()

    TOTAL_CPU_USAGE = auto()

    TOTAL_MEMORY = auto()

    AVAILABLE_MEMORY = auto()

    USED_MEMORY = auto()

    DURATION = auto()

    def __enum_header_name(self) -> str:
        enum_header_name = (
            enum_header_names_mapping[
                self
            ]
        )

        return enum_header_name

    enum_header_name = property(
        fget=__enum_header_name
    )


enum_header_names_mapping = {
    LogFunctionHeaderEnums.NOT_SET: str(),
    LogFunctionHeaderEnums.DATE_TIME: "date_time",
    LogFunctionHeaderEnums.LOGGING_TYPE: "logging_type",
    LogFunctionHeaderEnums.STACK_LEVEL: "stack_level",
    LogFunctionHeaderEnums.ACTION: "action",
    LogFunctionHeaderEnums.FUNCTION: "function",
    LogFunctionHeaderEnums.DISCRIMINATOR: "discriminator",
    LogFunctionHeaderEnums.TOTAL_CPU_USAGE: "total_cpu_usage (%)",
    LogFunctionHeaderEnums.TOTAL_MEMORY: "total_memory (GB)",
    LogFunctionHeaderEnums.AVAILABLE_MEMORY: "available_memory (GB)",
    LogFunctionHeaderEnums.USED_MEMORY: "used_memory (GB)",
    LogFunctionHeaderEnums.DURATION: "duration (s)",
}
