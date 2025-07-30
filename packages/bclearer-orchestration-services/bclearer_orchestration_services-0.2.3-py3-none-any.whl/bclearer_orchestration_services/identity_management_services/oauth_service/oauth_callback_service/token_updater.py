#!/usr/bin/env python3
"""
Script to exchange authorization codes for tokens and update them in the database.
This script can be run on a schedule to ensure we always have valid tokens.
"""
import argparse
import os
from datetime import datetime, timezone

from medical_data_b_clearer_pipeline.b_source.common.configurations.pipeline_config_loader import (
    load_environment_from_config,
)
from medical_data_b_clearer_pipeline.b_source.dexcom_pipeline.operations.dexcom_client import (
    DexcomClient,
)
from medical_data_b_clearer_pipeline.b_source.fitbit_pipeline.operations.fitbit_client import (
    FitbitClient,
)
from medical_data_b_clearer_pipeline.b_source.services.database_services.oauth_credential_store import (
    OAuthCredentialStore,
)


def update_dexcom_tokens(
    credential_store, config_file=None
):
    """
    Exchange Dexcom authorization code for tokens and store them.

    Args:
        credential_store: OAuthCredentialStore instance
        config_file: Optional path to config file
    """
    print(
        "\n=== Processing Dexcom tokens ==="
    )

    # Load configuration
    if config_file:
        load_environment_from_config(
            config_file
        )

    # Get stored credentials
    credentials = credential_store.get_credentials(
        "dexcom"
    )

    if not credentials:
        print(
            "No Dexcom credentials found in database."
        )
        return False

    # Check if we have an authorization code but no valid tokens
    if credentials.get(
        "authorization_code"
    ) and (
        not credentials.get(
            "access_token"
        )
        or credentials.get(
            "refresh_token"
        )
        == "pending_token_exchange"
    ):
        print(
            "Found authorization code without tokens - exchanging..."
        )
        # Set environment variables for DexcomClient
        os.environ[
            "DEXCOM_AUTHORIZATION_CODE"
        ] = credentials[
            "authorization_code"
        ]
        os.environ[
            "DEXCOM_REDIRECT_URI"
        ] = os.environ.get(
            "DEXCOM_REDIRECT_URI", ""
        )

        # Exchange code for tokens
        client = DexcomClient()
        token_data = (
            client.authenticate()
        )

        print(
            "Tokens obtained successfully."
        )
        return True

    # Check if tokens need refreshing
    elif (
        credentials.get("refresh_token")
        and credentials.get(
            "refresh_token"
        )
        != "pending_token_exchange"
    ):
        expires_at = credentials.get(
            "expires_at"
        )

        if (
            not expires_at
            or expires_at
            < datetime.now(timezone.utc)
        ):
            print(
                "Refresh token found but access token expired - refreshing..."
            )
            # Set environment variable for refresh
            os.environ[
                "DEXCOM_REFRESH_TOKEN"
            ] = credentials[
                "refresh_token"
            ]

            # Refresh tokens
            client = DexcomClient()
            token_data = (
                client.authenticate()
            )

            print(
                "Tokens refreshed successfully."
            )
            return True
        else:
            print(
                "Dexcom tokens are still valid."
            )
            return True

    print(
        "No suitable Dexcom credentials found for update."
    )
    return False


def update_fitbit_tokens(
    credential_store, config_file=None
):
    """
    Exchange Fitbit authorization code for tokens and store them.

    Args:
        credential_store: OAuthCredentialStore instance
        config_file: Optional path to config file
    """
    print(
        "\n=== Processing Fitbit tokens ==="
    )

    # Load configuration
    if config_file:
        load_environment_from_config(
            config_file
        )

    # Get stored credentials
    credentials = credential_store.get_credentials(
        "fitbit"
    )

    if not credentials:
        print(
            "No Fitbit credentials found in database."
        )
        return False

    # Check if we have an authorization code but no valid tokens
    if credentials.get(
        "authorization_code"
    ) and (
        not credentials.get(
            "access_token"
        )
        or credentials.get(
            "refresh_token"
        )
        == "pending_token_exchange"
    ):
        print(
            "Found authorization code without tokens - exchanging..."
        )
        # Set environment variables for FitbitClient
        os.environ[
            "FITBIT_AUTHORIZATION_CODE"
        ] = credentials[
            "authorization_code"
        ]
        os.environ[
            "FITBIT_REDIRECT_URI"
        ] = os.environ.get(
            "FITBIT_REDIRECT_URI", ""
        )

        # Exchange code for tokens
        try:
            client = FitbitClient()
            token_data = (
                client.authenticate()
            )

            print(
                "Tokens obtained successfully."
            )
            return True
        except Exception as e:
            print(
                f"Error exchanging Fitbit code for tokens: {e}"
            )
            return False

    # Check if tokens need refreshing
    elif (
        credentials.get("refresh_token")
        and credentials.get(
            "refresh_token"
        )
        != "pending_token_exchange"
    ):
        expires_at = credentials.get(
            "expires_at"
        )

        if (
            not expires_at
            or expires_at
            < datetime.now(timezone.utc)
        ):
            print(
                "Refresh token found but access token expired - refreshing..."
            )
            # Set environment variable for refresh
            os.environ[
                "FITBIT_REFRESH_TOKEN"
            ] = credentials[
                "refresh_token"
            ]

            # Refresh tokens
            try:
                client = FitbitClient()
                token_data = (
                    client.authenticate()
                )

                print(
                    "Tokens refreshed successfully."
                )
                return True
            except Exception as e:
                print(
                    f"Error refreshing Fitbit tokens: {e}"
                )
                return False
        else:
            print(
                "Fitbit tokens are still valid."
            )
            return True

    print(
        "No suitable Fitbit credentials found for update."
    )
    return False


def main(
    service="all", config_file=None
):
    """
    Main function to update tokens.

    Args:
        service: Service to update ('dexcom', 'fitbit', or 'all')
        config_file: Optional path to config file
    """
    print(
        "Starting token update process..."
    )

    # Load configuration
    if config_file:
        load_environment_from_config(
            config_file
        )

    # Initialize credential store
    try:
        credential_store = (
            OAuthCredentialStore()
        )
    except Exception as e:
        print(
            f"Error connecting to database: {e}"
        )
        return

    services_to_update = []
    if service.lower() == "all":
        services_to_update = [
            "dexcom",
            "fitbit",
        ]
    else:
        services_to_update = [
            service.lower()
        ]

    results = {}

    for svc in services_to_update:
        if svc == "dexcom":
            results["dexcom"] = (
                update_dexcom_tokens(
                    credential_store,
                    config_file,
                )
            )
        elif svc == "fitbit":
            results["fitbit"] = (
                update_fitbit_tokens(
                    credential_store,
                    config_file,
                )
            )

    # Close database connection
    credential_store.close()

    # Summary
    print(
        "\n=== Token Update Summary ==="
    )
    for svc, success in results.items():
        print(
            f"{svc.title()}: {'Success' if success else 'Failed/No update needed'}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OAuth Token Updater"
    )
    parser.add_argument(
        "--service",
        default="all",
        help="Service to update (dexcom, fitbit, or all)",
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file",
    )
    args = parser.parse_args()

    main(
        service=args.service,
        config_file=args.config,
    )
