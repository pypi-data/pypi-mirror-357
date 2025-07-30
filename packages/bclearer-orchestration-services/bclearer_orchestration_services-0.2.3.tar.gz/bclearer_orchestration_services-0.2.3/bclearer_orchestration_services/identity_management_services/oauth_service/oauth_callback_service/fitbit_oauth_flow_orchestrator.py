#!/usr/bin/env python3
"""
Script to perform OAuth 2.0 Authorization Code flow with Fitbit.

Usage:
  export FITBIT_CLIENT_ID=your_client_id
  export FITBIT_CLIENT_SECRET=your_client_secret
  export FITBIT_REDIRECT_URI=https://your_ngrok_url/callback
  # Optional, defaults:
  # export CALLBACK_HOST=0.0.0.0
  # export CALLBACK_PORT=8080

  python fitbit_oauth_flow_orchestrator.py
"""
import os
import sys
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime, timedelta

from flask import Flask, request
from medical_data_b_clearer_pipeline.b_source.fitbit_pipeline.operations.fitbit_client import (
    FitbitClient,
)
from medical_data_b_clearer_pipeline.b_source.services.database_services.oauth_credential_store import (
    OAuthCredentialStore,
)


def main():
    # Load configuration from JSON if present
    try:
        from medical_data_b_clearer_pipeline.b_source.common.configurations.pipeline_config_loader import (
            load_environment_from_config,
        )

        load_environment_from_config()
    except ImportError:
        pass
    client_id = os.getenv(
        "FITBIT_CLIENT_ID"
    )
    client_secret = os.getenv(
        "FITBIT_CLIENT_SECRET"
    )
    redirect_uri = os.getenv(
        "FITBIT_REDIRECT_URI"
    )
    if (
        not client_id
        or not client_secret
        or not redirect_uri
    ):
        print(
            "Please set FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET, and FITBIT_REDIRECT_URI environment variables."
        )
        sys.exit(1)

    host = os.getenv(
        "CALLBACK_HOST", "0.0.0.0"
    )
    port = int(
        os.getenv(
            "CALLBACK_PORT", "8080"
        )
    )

    parsed = urllib.parse.urlparse(
        redirect_uri
    )
    path = parsed.path or "/callback"

    state = {}

    app = Flask(__name__)

    @app.route(path)
    def callback():
        error = request.args.get(
            "error"
        )
        if error:
            return (
                f"Error: {error}",
                400,
            )
        code = request.args.get("code")
        if not code:
            return (
                "No code provided",
                400,
            )
        state["code"] = code
        shutdown = request.environ.get(
            "werkzeug.server.shutdown"
        )
        if shutdown:
            shutdown()
        return (
            "Authorization code received. You can close this window.",
            200,
        )

    server_thread = threading.Thread(
        target=lambda: app.run(
            host=host, port=port
        ),
        daemon=True,
    )
    server_thread.start()
    time.sleep(1)
    # Intraday access is handled separately through Fitbit's Developer Portal and doesn't use a specific OAuth scope
    default_scopes = "activity heartrate location nutrition oxygen_saturation profile respiratory_rate sleep temperature settings weight"
    authorize_endpoint = "https://www.fitbit.com/oauth2/authorize"
    scopes = os.getenv(
        "FITBIT_SCOPES", default_scopes
    )
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scopes,
    }
    auth_url = f"{authorize_endpoint}?{urllib.parse.urlencode(params)}"
    print(
        f"Open this URL in your browser to authorize the application:\n{auth_url}\n"
    )
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass
    print(
        f"Waiting for authorization code at http://{host}:{port}{path} ..."
    )

    while "code" not in state:
        time.sleep(1)

    code = state.get("code")
    print(
        f"\nReceived authorization code: {code}\n"
    )

    os.environ[
        "FITBIT_AUTHORIZATION_CODE"
    ] = code
    os.environ[
        "FITBIT_REDIRECT_URI"
    ] = redirect_uri
    client = FitbitClient()
    token_data = client.authenticate()

    print("\nToken data:")
    print(token_data)

    # Store credentials in PostgreSQL database
    credential_store = (
        OAuthCredentialStore()
    )

    if (
        hasattr(client, "refresh_token")
        and client.refresh_token
    ):
        # Calculate token expiration time
        expires_in = token_data.get(
            "expires_in", 0
        )
        expires_at = (
            datetime.utcnow()
            + timedelta(
                seconds=expires_in
            )
            if expires_in
            else None
        )

        # Store in database
        credential_store.store_credentials(
            service="fitbit",
            authorization_code=code,
            access_token=token_data.get(
                "access_token"
            ),
            refresh_token=client.refresh_token,
            expires_at=expires_at,
        )

        print(
            "\nCredentials stored in database successfully."
        )
        print(
            f"\nSave this refresh token for future runs:\n{client.refresh_token}"
        )
    else:
        print(
            "\nNo refresh token returned. Ensure you requested proper scopes."
        )


if __name__ == "__main__":
    main()
