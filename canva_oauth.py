"""Secure rotating Canva Connect OAuth refresh-token storage for GitHub Actions.

The official Canva refresh_token is SINGLE-USE. Persist each new token in
strongly encrypted repository state and push it *before* attempting an export.
The encryption key and the one-time bootstrap refresh token stay in Secrets.
Never log bearer tokens, URLs with credentials, or decrypted refresh tokens.
"""
import os
from pathlib import Path
import subprocess
import time

import requests
from cryptography.fernet import Fernet, InvalidToken

ENC_PATH = Path("state/canva/refresh_token.enc")
CANVA_TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"


class CanvaOAuthSetupRequired(RuntimeError):
    pass


def persist_refresh_token(encrypted_file):
    """Durably commit encrypted token before any further Canva API calls."""
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email",
                    "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "--", str(encrypted_file)], check=True)
    subprocess.run(["git", "commit", "-m", "Rotate encrypted Canva OAuth refresh token"],
                   check=True)
    for _ in range(3):
        try:
            subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
            subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
            return
        except subprocess.CalledProcessError:
            time.sleep(3)
    raise RuntimeError("Canva OAuth rotated but encrypted credential could not be "
                       "persisted. Publishing is blocked; reconnect to Canva safely.")


def get_access_token():
    """Exchange a saved single-use refresh token for a fresh access token."""
    if os.getenv("CANVA_ACCESS_TOKEN") and not os.getenv("CANVA_REFRESH_TOKEN"):
        # A short-term diagnostic only. It expires in ~4 hours; not for 5/day automation.
        return os.getenv("CANVA_ACCESS_TOKEN")
    key = os.getenv("CANVA_TOKEN_KEY", "")
    client_id = os.getenv("CANVA_CLIENT_ID", "")
    client_secret = os.getenv("CANVA_CLIENT_SECRET", "")
    first_refresh = os.getenv("CANVA_REFRESH_TOKEN", "")
    if not (key and client_id and client_secret):
        raise CanvaOAuthSetupRequired(
            "Canva Connect OAuth integration is not configured. Canva-only publishing stays paused."
        )
    try:
        cipher = Fernet(key.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise CanvaOAuthSetupRequired("Invalid Canva token-encryption key") from exc
    if os.getenv("CANVA_OAUTH_REAUTHORIZE_FROM_SECRET") == "YES":
        if not first_refresh:
            raise CanvaOAuthSetupRequired("A newly authorized CANVA_REFRESH_TOKEN secret is required")
        old_refresh = first_refresh
    elif ENC_PATH.exists():
        try:
            old_refresh = cipher.decrypt(ENC_PATH.read_bytes()).decode("utf-8")
        except (InvalidToken, UnicodeError) as exc:
            raise RuntimeError(
                "Cannot decrypt stored Canva refresh token; reauthorization required"
            ) from exc
    elif first_refresh:
        old_refresh = first_refresh
    else:
        raise CanvaOAuthSetupRequired("Initial Canva OAuth refresh token is missing")
    try:
        response = requests.post(CANVA_TOKEN_URL,
                                 auth=(client_id, client_secret),
                                 data={"grant_type": "refresh_token",
                                       "refresh_token": old_refresh},
                                 timeout=30)
        if not response.ok:
            try:
                detail = response.json()
            except ValueError:
                detail = {}
            code = detail.get("error", detail.get("code", "unknown"))
            allowed = {"invalid_grant", "invalid_client", "invalid_request", "unauthorized_client", "unsupported_grant_type", "invalid_refresh_token"}
            safe_code = code if isinstance(code, str) and code in allowed else "unclassified"
            raise RuntimeError(
                f"Canva token refresh failed (HTTP {response.status_code}, code={safe_code}); no automatic retry"
            )
        obj = response.json()
        token = obj.get("access_token")
        new_refresh = obj.get("refresh_token")
        if not token or not new_refresh:
            raise RuntimeError("Canva OAuth response lacks access or refresh token")
        ENC_PATH.parent.mkdir(parents=True, exist_ok=True)
        temp = ENC_PATH.with_suffix(".new")
        temp.write_bytes(cipher.encrypt(new_refresh.encode("utf-8")))
        os.chmod(temp, 0o600)
        temp.replace(ENC_PATH)
        # Must persist before using the newly rotated token, to survive later errors.
        persist_refresh_token(ENC_PATH)
        return token
    except requests.RequestException as exc:
        raise RuntimeError(
            "Canva OAuth connection failed: " + type(exc).__name__
        ) from exc
