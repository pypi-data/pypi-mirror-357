import logging


class StandardLoggingProcessConsoleHandlers(
    logging.StreamHandler
):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(
                msg + self.terminator
            )
            self.flush()
        except (
            RecursionError
        ):  # See issue 36272
            raise
        except Exception:
            self.handleError(record)
