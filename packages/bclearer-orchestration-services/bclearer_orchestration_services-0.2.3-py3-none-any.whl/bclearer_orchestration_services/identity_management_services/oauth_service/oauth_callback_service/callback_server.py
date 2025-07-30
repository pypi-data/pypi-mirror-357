"""
OAuth callback server catching OAuth redirects with authorization codes.
Stores authorization codes to a PostgreSQL database.
"""

import argparse
import os

from flask import Flask, request
from medical_data_b_clearer_pipeline.b_source.common.configurations.pipeline_config_loader import (
    load_environment_from_config,
)
from medical_data_b_clearer_pipeline.b_source.services.database_services.oauth_credential_store import (
    OAuthCredentialStore,
)


def create_app(db_store=None):
    """
    Create and configure the Flask application for OAuth callback.

    Args:
        db_store: Optional OAuthCredentialStore instance
    """
    app = Flask(__name__)

    # Initialize database connection if not provided
    if db_store is None:
        try:
            # Load configuration and initialize credential store
            load_environment_from_config()
            db_store = (
                OAuthCredentialStore()
            )
            print(
                "Database connection established"
            )
        except Exception as e:
            print(
                f"Warning: Could not initialize database connection: {e}"
            )
            print(
                "Authorization codes will be printed but not stored."
            )
            db_store = None

    @app.route("/")
    def root_callback():
        """
        Handle root path redirects. Detects whether it's from Fitbit or Dexcom.
        """
        code = request.args.get("code")
        if not code:
            return (
                "⚠️ No code parameter found in redirect.",
                400,
            )

        # Check query params or headers to determine which service this is from
        # For now we'll assume it's from Fitbit if it matches the Fitbit code pattern (hex only)
        if code and all(
            c in "0123456789abcdef"
            for c in code.lower()
        ):
            print(
                f"\n⤷ Detected Fitbit auth code at root path: {code}"
            )
            service = "fitbit"
            # Store in database if connection available
            if db_store is not None:
                try:
                    # Check if entry exists
                    existing = db_store.get_credentials(
                        service
                    )
                    if (
                        existing
                        and existing.get(
                            "refresh_token"
                        )
                        and existing.get(
                            "refresh_token"
                        )
                        != "pending_token_exchange"
                    ):
                        # Update existing credential with new auth code
                        db_store.store_credentials(
                            service=service,
                            refresh_token=existing[
                                "refresh_token"
                            ],
                            authorization_code=code,
                            access_token=existing.get(
                                "access_token"
                            ),
                            expires_at=existing.get(
                                "expires_at"
                            ),
                        )
                    else:
                        # Initialize with auth code only
                        db_store.store_credentials(
                            service=service,
                            refresh_token="pending_token_exchange",
                            authorization_code=code,
                        )
                    print(
                        f"✅ Fitbit authorization code saved to database for service: {service}"
                    )
                except Exception as e:
                    print(
                        f"Error storing authorization code: {e}"
                    )

            # Set environment variable for local use
            os.environ[
                "FITBIT_AUTHORIZATION_CODE"
            ] = code
            return (
                "✅ Fitbit authorization code received and stored. You can close this window.",
                200,
            )
        else:
            # Assume Dexcom for any other code format
            print(
                f"\n⤷ Detected Dexcom auth code at root path: {code}"
            )
            service = "dexcom"
            if db_store is not None:
                try:
                    # Check if entry exists
                    existing = db_store.get_credentials(
                        service
                    )
                    if (
                        existing
                        and existing.get(
                            "refresh_token"
                        )
                        and existing.get(
                            "refresh_token"
                        )
                        != "pending_token_exchange"
                    ):
                        # Update existing credential with new auth code
                        db_store.store_credentials(
                            service=service,
                            refresh_token=existing[
                                "refresh_token"
                            ],
                            authorization_code=code,
                            access_token=existing.get(
                                "access_token"
                            ),
                            expires_at=existing.get(
                                "expires_at"
                            ),
                        )
                    else:
                        # Initialize with auth code only
                        db_store.store_credentials(
                            service=service,
                            refresh_token="pending_token_exchange",
                            authorization_code=code,
                        )
                    print(
                        f"✅ Dexcom authorization code saved to database for service: {service}"
                    )
                except Exception as e:
                    print(
                        f"Error storing authorization code: {e}"
                    )

            # Set environment variable for local use
            os.environ[
                "DEXCOM_AUTHORIZATION_CODE"
            ] = code
            return (
                "✅ Dexcom authorization code received and stored. You can close this window.",
                200,
            )

    @app.route("/dexcom_callback")
    @app.route("/callback")
    def dexcom_callback():
        """
        Handle the OAuth2 redirect for Dexcom by extracting the 'code' parameter.
        Stores it to PostgreSQL if database connection is available.
        """
        service = "dexcom"
        code = request.args.get("code")
        if code:
            print(
                f"\n⤷ Dexcom auth code: {code}"
            )

            # Store in database if connection available
            if db_store is not None:
                try:
                    # Check if entry exists
                    existing = db_store.get_credentials(
                        service
                    )
                    if (
                        existing
                        and existing.get(
                            "refresh_token"
                        )
                        and existing.get(
                            "refresh_token"
                        )
                        != "pending_token_exchange"
                    ):
                        # Update existing credential with new auth code
                        db_store.store_credentials(
                            service=service,
                            refresh_token=existing[
                                "refresh_token"
                            ],
                            authorization_code=code,
                            access_token=existing.get(
                                "access_token"
                            ),
                            expires_at=existing.get(
                                "expires_at"
                            ),
                        )
                    else:
                        # Initialize with auth code only
                        db_store.store_credentials(
                            service=service,
                            refresh_token="pending_token_exchange",
                            authorization_code=code,
                        )
                    print(
                        f"✅ Dexcom authorization code saved to database for service: {service}"
                    )
                except Exception as e:
                    print(
                        f"Error storing authorization code: {e}"
                    )

            # Set environment variable for local use
            os.environ[
                "DEXCOM_AUTHORIZATION_CODE"
            ] = code
            return (
                "✅ Dexcom authorization code received and stored. You can close this window.",
                200,
            )

        return (
            "⚠️ No code parameter found in Dexcom redirect.",
            400,
        )

    @app.route("/fitbit_callback")
    def fitbit_callback():
        """
        Handle the OAuth2 redirect for Fitbit by extracting the 'code' parameter.
        Stores it to PostgreSQL if database connection is available.
        """
        service = "fitbit"
        code = request.args.get("code")
        if code:
            print(
                f"\n⤷ Fitbit auth code: {code}"
            )

            # Store in database if connection available
            if db_store is not None:
                try:
                    # Check if entry exists
                    existing = db_store.get_credentials(
                        service
                    )
                    if (
                        existing
                        and existing.get(
                            "refresh_token"
                        )
                        and existing.get(
                            "refresh_token"
                        )
                        != "pending_token_exchange"
                    ):
                        # Update existing credential with new auth code
                        db_store.store_credentials(
                            service=service,
                            refresh_token=existing[
                                "refresh_token"
                            ],
                            authorization_code=code,
                            access_token=existing.get(
                                "access_token"
                            ),
                            expires_at=existing.get(
                                "expires_at"
                            ),
                        )
                    else:
                        # Initialize with auth code only
                        db_store.store_credentials(
                            service=service,
                            refresh_token="pending_token_exchange",
                            authorization_code=code,
                        )
                    print(
                        f"✅ Fitbit authorization code saved to database for service: {service}"
                    )
                except Exception as e:
                    print(
                        f"Error storing authorization code: {e}"
                    )

            # Set environment variable for local use
            os.environ[
                "FITBIT_AUTHORIZATION_CODE"
            ] = code
            return (
                "✅ Fitbit authorization code received and stored. You can close this window.",
                200,
            )

        return (
            "⚠️ No code parameter found in Fitbit redirect.",
            400,
        )

    @app.route("/health")
    def health_check():
        """
        Simple health check endpoint.
        """
        db_status = (
            "Connected"
            if db_store is not None
            else "Not connected"
        )
        return (
            f"OAuth Callback Server is running. Database status: {db_status}",
            200,
        )

    return app


def run_callback_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    config_file: str = None,
):
    """
    Run the Flask callback server on the given host and port.

    Args:
        host: Hostname to listen on
        port: Port to listen on
        config_file: Path to configuration file
    """
    # Load configuration if provided
    if config_file:
        load_environment_from_config(
            config_file
        )

    # Initialize database connection
    try:
        db_store = (
            OAuthCredentialStore()
        )
        print(
            "Database connection established"
        )
    except Exception as e:
        print(
            f"Warning: Could not initialize database connection: {e}"
        )
        print(
            "Authorization codes will be printed but not stored."
        )
        db_store = None

    # Create and run app
    app = create_app(db_store)
    print(
        f"Starting OAuth callback server on http://{host}:{port}"
    )
    print(
        f"Listening for callbacks on:"
    )
    print(
        f"  - http://{host}:{port}/ (Root path - auto-detects service)"
    )
    print(
        f"  - http://{host}:{port}/callback (Dexcom)"
    )
    print(
        f"  - http://{host}:{port}/dexcom_callback (Dexcom alternative)"
    )
    print(
        f"  - http://{host}:{port}/fitbit_callback (Fitbit)"
    )
    app.run(host=host, port=port)


if (
    __name__ == "__main__"
):  # pragma: no cover
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="OAuth Callback Server"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to listen on",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on",
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file",
    )
    args = parser.parse_args()

    # Run server with provided arguments
    run_callback_server(
        host=args.host,
        port=args.port,
        config_file=args.config,
    )
