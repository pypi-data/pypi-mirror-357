import logging
import sqlite3
from datetime import datetime


class StandardLoggingProcessSQLiteHandlers(
    logging.Handler
):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.connection = (
            sqlite3.connect(
                self.db_path
            )
        )
        self._create_table()

    def _create_table(self):
        """Create the logs table if it doesn't exist."""
        cursor = (
            self.connection.cursor()
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT,
                level TEXT,
                stack_level TEXT,
                function_name TEXT,
                function_discriminator_name TEXT,
                total_cpu_usage TEXT,
                total_memory TEXT,
                available_memory TEXT,
                used_memory TEXT,
                event TEXT,
                logged TEXT,
                duration TEXT,
                module TEXT,
                funcName TEXT,
                lineNo INTEGER
            )
        """
        )
        self.connection.commit()

    def emit(self, record):
        """Insert a log record into the SQLite database."""
        cursor = (
            self.connection.cursor()
        )

        try:
            if isinstance(
                record.msg, dict
            ):
                message = record.msg
            else:
                raise TypeError

            if (
                "duration"
                not in message
            ):
                message["duration"] = ""

            cursor.execute(
                """
                INSERT INTO logs (created, level, stack_level, function_name, function_discriminator_name, total_cpu_usage ,total_memory ,available_memory ,used_memory ,event ,logged ,duration, module, funcName, lineNo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),  # Format timestamp
                    record.levelname,
                    message[
                        "stack_level"
                    ],
                    message[
                        "function_name"
                    ],
                    message[
                        "function_discriminator_name"
                    ],
                    message[
                        "total_cpu_usage"
                    ],
                    message[
                        "total_memory"
                    ],
                    message[
                        "available_memory"
                    ],
                    message[
                        "used_memory"
                    ],
                    message["event"],
                    message["logged"],
                    message["duration"],
                    record.module,
                    record.funcName,
                    record.lineno,
                ),
            )
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(
                f"Failed to log message: {e}"
            )
        finally:
            cursor.close()

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
        super().close()
