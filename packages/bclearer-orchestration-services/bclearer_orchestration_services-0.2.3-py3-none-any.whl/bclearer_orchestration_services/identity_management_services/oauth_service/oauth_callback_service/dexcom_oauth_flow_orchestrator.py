#!/usr/bin/env python3
"""
Script to perform OAuth 2.0 Authorization Code flow with Dexcom.

Usage:
  export DEXCOM_CLIENT_ID=your_client_id
  export DEXCOM_CLIENT_SECRET=your_client_secret
  export DEXCOM_REDIRECT_URI=https://your_ngrok_url/callback
  # Optional, defaults:
  # export CALLBACK_HOST=0.0.0.0
  # export CALLBACK_PORT=8080

  python dexcom_oauth_flow_orchestrator.py
"""
import os
import sys
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime, timedelta

from flask import Flask, request
from medical_data_b_clearer_pipeline.b_source.dexcom_pipeline.operations.dexcom_client import (
    DexcomClient,
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
    # Ensure required environment variables
    client_id = os.getenv(
        "DEXCOM_CLIENT_ID"
    )
    client_secret = os.getenv(
        "DEXCOM_CLIENT_SECRET"
    )
    redirect_uri = os.getenv(
        "DEXCOM_REDIRECT_URI"
    )
    if (
        not client_id
        or not client_secret
        or not redirect_uri
    ):
        print(
            "Please set DEXCOM_CLIENT_ID, DEXCOM_CLIENT_SECRET, and DEXCOM_REDIRECT_URI environment variables."
        )
        sys.exit(1)

    # Host and port where local callback server listens (ngrok forwards here)
    host = os.getenv(
        "CALLBACK_HOST", "0.0.0.0"
    )
    port = int(
        os.getenv(
            "CALLBACK_PORT", "8080"
        )
    )

    # Determine redirect path from URI
    parsed = urllib.parse.urlparse(
        redirect_uri
    )
    path = parsed.path or "/callback"

    # Shared state for storing authorization code
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
        # store code and shut down server
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

    # Start callback server in background
    server_thread = threading.Thread(
        target=lambda: app.run(
            host=host, port=port
        ),
        daemon=True,
    )
    server_thread.start()
    time.sleep(
        1
    )  # wait for server to be ready

    # Build and open authorization URL
    client = (
        DexcomClient()
    )  # debug prints
    authorize_endpoint = f"{client.base_url}/v2/oauth2/login"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "offline_access",
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

    # Wait until code is captured
    while "code" not in state:
        time.sleep(1)

    code = state.get("code")
    print(
        f"\nReceived authorization code: {code}\n"
    )

    # Exchange code for tokens
    os.environ[
        "DEXCOM_AUTHORIZATION_CODE"
    ] = code
    os.environ[
        "DEXCOM_REDIRECT_URI"
    ] = redirect_uri
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
            service="dexcom",
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
            "\nNo refresh token returned. Ensure you requested 'offline_access' scope."
        )


if __name__ == "__main__":
    main()
