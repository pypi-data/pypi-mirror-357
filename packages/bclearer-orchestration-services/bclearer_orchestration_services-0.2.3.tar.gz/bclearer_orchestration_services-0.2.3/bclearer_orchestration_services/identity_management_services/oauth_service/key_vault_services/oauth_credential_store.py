"""
OAuth credential storage service for PostgreSQL databases.
Uses bclearer_interop_services package to interact with PostgreSQL.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bclearer_interop_services.relational_database_services.postgresql.PostgresqlFacade import (
    PostgresqlFacade,
)
from medical_data_b_clearer_pipeline.b_source.common.configurations.pipeline_config_loader import (
    load_environment_from_config,
)
from medical_data_b_clearer_pipeline.b_source.common.configurations.pipeline_config_manager import (
    get_configuration,
)


class OAuthCredentialStore:
    """
    Store and retrieve OAuth credentials using PostgreSQL.
    """

    def __init__(self):
        self._db = None
        # Reload environment from config file to ensure we have latest values
        load_environment_from_config()
        # Initialize database connection
        self._ensure_db_facade()
        self._ensure_table_exists()

    def _ensure_db_facade(self) -> None:
        """
        Create and configure the PostgreSQL database facade.
        """
        if self._db is not None:
            return

        # Get connection parameters from environment variables first, then fallback to default
        host = os.environ.get(
            "POSTGRES_HOST",
            "192.168.0.36",
        )
        port = os.environ.get(
            "POSTGRES_PORT", "5432"
        )
        database = os.environ.get(
            "POSTGRES_DATABASE",
            "medical_data",
        )
        user = os.environ.get(
            "POSTGRES_USER", "ladmin"
        )
        password = os.environ.get(
            "POSTGRES_PASSWORD",
            "Numark234",
        )

        # Debug connection params
        print(
            "PostgreSQL Connection Parameters:"
        )
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Database: {database}")
        print(f"  User: {user}")
        print(
            f"  Password: {'*' * len(password) if password else 'Not set'}"
        )

        # Create PostgresqlFacade with required parameters
        self._db = PostgresqlFacade(
            host=host,
            database=database,
            user=user,
            password=password,
        )

        # Set port if specified
        if port:
            self._db.port = port

        # Connect to database
        self._db.connect()
        print(
            "Successfully connected to PostgreSQL database"
        )

    def _ensure_table_exists(
        self,
    ) -> None:
        """
        Create the OAuth credentials table if it doesn't exist.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS oauth_credentials (
            id SERIAL PRIMARY KEY,
            service VARCHAR(50) NOT NULL,
            authorization_code TEXT,
            access_token TEXT,
            refresh_token TEXT NOT NULL,
            expires_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(service)
        );

        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE tablename = 'oauth_credentials'
                AND indexname = 'oauth_credentials_service_idx'
            ) THEN
                CREATE INDEX oauth_credentials_service_idx ON oauth_credentials(service);
            END IF;
        END$$;
        """

        try:
            self._db.execute_query(
                create_table_sql
            )
            print(
                "OAuth credentials table verified/created"
            )
        except Exception as e:
            print(
                f"Error creating oauth_credentials table: {e}"
            )
            raise

    def store_credentials(
        self,
        service: str,
        refresh_token: str,
        authorization_code: Optional[
            str
        ] = None,
        access_token: Optional[
            str
        ] = None,
        expires_at: Optional[
            datetime
        ] = None,
    ) -> bool:
        """
        Store OAuth credentials for a service.
        If the service already exists, credentials will be updated.

        Args:
            service: Service identifier ('dexcom' or 'fitbit')
            refresh_token: OAuth refresh token
            authorization_code: OAuth authorization code
            access_token: OAuth access token
            expires_at: Token expiration datetime

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if service already exists
            check_sql = """
            SELECT id FROM oauth_credentials WHERE service = %s
            """
            results = (
                self._db.fetch_results(
                    check_sql, [service]
                )
            )

            if len(results) > 0:
                # Update existing entry
                update_sql = """
                UPDATE oauth_credentials
                SET refresh_token = %s,
                    authorization_code = %s,
                    access_token = %s,
                    expires_at = %s,
                    updated_at = NOW()
                WHERE service = %s
                """
                self._db.execute_query(
                    update_sql,
                    [
                        refresh_token,
                        authorization_code,
                        access_token,
                        expires_at,
                        service,
                    ],
                )
                print(
                    f"Updated OAuth credentials for service: {service}"
                )
            else:
                # Insert new entry
                insert_sql = """
                INSERT INTO oauth_credentials
                    (service, authorization_code, access_token, refresh_token, expires_at)
                VALUES (%s, %s, %s, %s, %s)
                """
                self._db.execute_query(
                    insert_sql,
                    [
                        service,
                        authorization_code,
                        access_token,
                        refresh_token,
                        expires_at,
                    ],
                )
                print(
                    f"Inserted new OAuth credentials for service: {service}"
                )

            return True
        except Exception as e:
            print(
                f"Error storing OAuth credentials: {e}"
            )
            return False

    def get_credentials(
        self, service: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get OAuth credentials for a service.

        Args:
            service: Service identifier ('dexcom' or 'fitbit')

        Returns:
            Dictionary with credential information or None if not found
        """
        try:
            query = """
            SELECT
                service,
                authorization_code,
                access_token,
                refresh_token,
                expires_at
            FROM oauth_credentials
            WHERE service = %s
            """
            results = (
                self._db.fetch_results(
                    query, [service]
                )
            )

            if len(results) == 0:
                return None

            row = results.iloc[0]
            return {
                "service": row[
                    "service"
                ],
                "authorization_code": row[
                    "authorization_code"
                ],
                "access_token": row[
                    "access_token"
                ],
                "refresh_token": row[
                    "refresh_token"
                ],
                "expires_at": row[
                    "expires_at"
                ],
            }
        except Exception as e:
            print(
                f"Error retrieving OAuth credentials: {e}"
            )
            return None

    def update_tokens(
        self,
        service: str,
        access_token: str,
        refresh_token: str,
        expires_at: Optional[
            datetime
        ] = None,
    ) -> bool:
        """
        Update access and refresh tokens for a service.

        Args:
            service: Service identifier ('dexcom' or 'fitbit')
            access_token: New access token
            refresh_token: New refresh token
            expires_at: New token expiration datetime

        Returns:
            True if successful, False otherwise
        """
        try:
            update_sql = """
            UPDATE oauth_credentials
            SET access_token = %s,
                refresh_token = %s,
                expires_at = %s,
                updated_at = NOW()
            WHERE service = %s
            """
            self._db.execute_query(
                update_sql,
                [
                    access_token,
                    refresh_token,
                    expires_at,
                    service,
                ],
            )
            return True
        except Exception as e:
            print(
                f"Error updating OAuth tokens: {e}"
            )
            return False

    def set_environment_variables(
        self, service: str
    ) -> bool:
        """
        Set environment variables from stored credentials.

        Args:
            service: Service identifier ('dexcom' or 'fitbit')

        Returns:
            True if successful, False otherwise
        """
        credentials = (
            self.get_credentials(
                service
            )
        )
        if not credentials:
            return False

        if service.lower() == "dexcom":
            prefix = "DEXCOM"
        elif (
            service.lower() == "fitbit"
        ):
            prefix = "FITBIT"
        else:
            return False

        if credentials[
            "authorization_code"
        ]:
            os.environ[
                f"{prefix}_AUTHORIZATION_CODE"
            ] = credentials[
                "authorization_code"
            ]

        if credentials["refresh_token"]:
            os.environ[
                f"{prefix}_REFRESH_TOKEN"
            ] = credentials[
                "refresh_token"
            ]

        return True

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self._db:
            self._db.disconnect()
