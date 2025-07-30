import logging


class StandardLoggingProcessFlatFormatters(
    logging.Formatter
):
    def format(self, record):
        # Check if the original message is a dictionary
        if isinstance(record.msg, dict):
            # Create a custom formatted string for the message
            message = "¬".join(
                f"{value}"
                for key, value in record.msg.items()
            )
            # Temporarily set record.message to the formatted string
            record.message = message
        else:
            # Use the default message formatting
            record.message = (
                record.getMessage()
            )

        # Return the formatted log entry
        return (
            self._fmt % record.__dict__
        )
