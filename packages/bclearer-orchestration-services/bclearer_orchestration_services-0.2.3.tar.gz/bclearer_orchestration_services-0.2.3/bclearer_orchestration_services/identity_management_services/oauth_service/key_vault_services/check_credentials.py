#!/usr/bin/env python3
"""
Script to check stored OAuth credentials in the PostgreSQL database.

Usage:
  python check_credentials.py --service dexcom
  python check_credentials.py --service fitbit
  python check_credentials.py --service all
"""
import argparse

from medical_data_b_clearer_pipeline.b_source.common.configurations.pipeline_config_loader import (
    load_environment_from_config,
)
from medical_data_b_clearer_pipeline.b_source.services.key_vault_services.oauth_credential_store import (
    OAuthCredentialStore,
)


def check_credentials(
    service="all", config_file=None
):
    """
    Check stored OAuth credentials for specified services.

    Args:
        service: Service name ('dexcom', 'fitbit', or 'all')
        config_file: Optional path to config file
    """
    print(
        f"Checking OAuth credentials for: {service}"
    )

    # Load configuration
    if config_file:
        load_environment_from_config(
            config_file
        )

    # Create credential store
    store = OAuthCredentialStore()

    services_to_check = []
    if service.lower() == "all":
        services_to_check = [
            "dexcom",
            "fitbit",
        ]
    else:
        services_to_check = [
            service.lower()
        ]

    for svc in services_to_check:
        print(
            f"\n--- {svc.upper()} Credentials ---"
        )

        # Get credentials from database
        credentials = (
            store.get_credentials(svc)
        )

        if not credentials:
            print(
                f"No credentials found for {svc}"
            )
            continue

        print(
            f"Service: {credentials['service']}"
        )
        print(
            f"Authorization Code: {'*' * 8 if credentials['authorization_code'] else 'None'}"
        )
        print(
            f"Access Token: {'*' * 8 if credentials['access_token'] else 'None'}"
        )
        print(
            f"Refresh Token: {'*' * 8 if credentials['refresh_token'] else 'None'}"
        )
        print(
            f"Expires At: {credentials['expires_at']}"
        )

    # Close connection
    store.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check stored OAuth credentials"
    )
    parser.add_argument(
        "--service",
        help="Service name (dexcom, fitbit, or all)",
        default="all",
    )
    parser.add_argument(
        "--config",
        help="Path to configuration JSON file",
        default=None,
    )
    args = parser.parse_args()

    check_credentials(
        args.service, args.config
    )
