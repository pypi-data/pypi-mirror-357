#!/usr/bin/env python3
"""
Script to initialize PostgreSQL database for OAuth credential storage.

Usage:
  python init_db.py
"""
import argparse

from medical_data_b_clearer_pipeline.b_source.common.configurations.pipeline_config_loader import (
    load_environment_from_config,
)
from medical_data_b_clearer_pipeline.b_source.services.key_vault_services.oauth_credential_store import (
    OAuthCredentialStore,
)


def initialize_database(
    config_file=None,
):
    """
    Initialize PostgreSQL database for OAuth credential storage.

    Args:
        config_file: Optional path to config file with PostgreSQL connection details
    """
    print(
        "Initializing OAuth credential database..."
    )

    # Load configuration
    if config_file:
        load_environment_from_config(
            config_file
        )

    try:
        # Create credential store (this automatically creates the table)
        store = OAuthCredentialStore()

        # Output connection details for verification
        host = store._db.host
        port = (
            store._db.port
            if hasattr(
                store._db, "port"
            )
            else "5432"
        )  # Default PostgreSQL port
        database = store._db.database
        user = store._db.user

        print(
            "Database initialized successfully."
        )
        print("Connection parameters:")
        print(f"  Host: {host}")
        print(f"  Port: {port}")
        print(f"  Database: {database}")
        print(f"  User: {user}")
        print(
            "Table 'oauth_credentials' is ready for use."
        )

        # Close connection
        store.close()

    except Exception as e:
        print(
            f"Error initializing database: {e}"
        )
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize PostgreSQL database for OAuth credential storage"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration JSON file",
        default=None,
    )
    args = parser.parse_args()

    initialize_database(args.config)
