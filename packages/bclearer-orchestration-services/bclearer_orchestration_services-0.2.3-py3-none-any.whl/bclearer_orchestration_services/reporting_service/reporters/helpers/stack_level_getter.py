import inspect


def get_stack_level() -> str:
    stack = inspect.stack()

    stack_level_as_string = str(
        len(stack)
    )

    return stack_level_as_string
