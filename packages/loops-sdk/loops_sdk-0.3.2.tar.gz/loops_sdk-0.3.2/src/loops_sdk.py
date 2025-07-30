"""loops_sdk.py
Python SDK for Loops (https://loops.so)

This implementation mirrors the public interface of the official TypeScript SDK.
All endpoints, error handling behaviour and payload shapes follow the public REST documentation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, List, Union

import re
from dataclasses import dataclass, field
import requests

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Public error types
# ---------------------------------------------------------------------------
class RateLimitExceededError(Exception):
    """Raised when the Loops API returns HTTP 429."""

    def __init__(self, limit: int, remaining: int):
        super().__init__(f"Rate limit of {limit} requests per second exceeded.")
        self.limit = limit
        self.remaining = remaining


class APIError(Exception):
    """Raised when the Loops API returns any non-2xx response (except 429)."""

    def __init__(self, status_code: int, json: Any):
        # The response body *should* be a JSON object, but in tests or edge
        # cases we may receive other python objects (e.g. a Mock instance or a
        # plain string).  Guard against this so that str() inspection never
        # raises its own error.
        message: str | None = None
        if isinstance(json, dict):
            if "error" in json and isinstance(json["error"], dict):
                message = json["error"].get("message")
            elif "error" in json and isinstance(json["error"], str):
                message = json["error"]
            elif "message" in json:
                message = json["message"]
        else:
            # Fallback: just coerce to string so that the exception at least
            # carries *some* context for debugging.
            message = str(json)
        super().__init__(f"{status_code}{f' – {message}' if message else ''}")
        self.status_code = status_code
        self.json = json


class ValidationError(Exception):
    """Raised when the SDK detects invalid arguments before making a request."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Attachment:
    """Represents a single file attachment for a transactional email."""

    filename: str
    content_type: str
    data: str  # Base-64 encoded payload

    def to_dict(self) -> Dict[str, str]:  # noqa: D401 (simple helper)
        """Return a Loops-compatible dictionary representation of the attachment."""
        return {
            "filename": self.filename,
            "contentType": self.content_type,
            "data": self.data,
        }


@dataclass(frozen=True)
class LoopsEmail:
    """Container for all parameters required to send a transactional email."""

    email: str
    transactional_id: str
    add_to_audience: Optional[bool] = None
    data_variables: Optional[Dict[str, Union[str, int]]] = None
    attachments: List[Attachment] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:  # noqa: D401
        """Convert the dataclass to the exact payload expected by the Loops API."""
        payload = {
            "email": self.email,
            "transactionalId": self.transactional_id,
        }
        if self.add_to_audience is not None:
            payload["addToAudience"] = self.add_to_audience
        if self.data_variables is not None:
            payload["dataVariables"] = self.data_variables
        if self.attachments:
            payload["attachments"] = [a.to_dict() for a in self.attachments]
        return payload


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
_email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _validate_email(email: str) -> None:  # noqa: D401 (simple helper)
    """Raise ``TypeError`` if *email* is not a valid email address."""
    if not isinstance(email, str) or not _email_pattern.match(email):
        raise TypeError("'email' must be a valid email address.")

# ---------------------------------------------------------------------------
# Loops API client (sync, Requests-based)
# ---------------------------------------------------------------------------
class LoopsClient:
    """Lightweight synchronous Loops API client.

    Mirrors the public surface of the official TypeScript SDK, but uses Pythonic
    snake_case method names. A camelCase alias is provided for
    `send_transactional_email` to minimise change friction when porting code.
    """

    def __init__(self, api_key: str, api_root: str = "https://app.loops.so/api/") -> None:
        # Normalise API root so that urljoin works as expected
        if not api_root.endswith("/"):
            api_root += "/"
        self.api_root = api_root

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
        )

    # ---------------------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------------------
    def _make_query(
        self,
        *,
        path: str,
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = requests.compat.urljoin(self.api_root, path)
        h = self.session.headers.copy()
        if headers:
            h.update({k: v for k, v in headers.items() if v})

        resp = self.session.request(method, url, json=payload if payload is not None else None, params=params, headers=h)

        if resp.status_code == 429:
            limit = int(resp.headers.get("x-ratelimit-limit", "10"))
            remaining = int(resp.headers.get("x-ratelimit-remaining", "0"))
            raise RateLimitExceededError(limit, remaining)

        if resp.status_code >= 400:
            try:
                data = resp.json()
            except ValueError:
                data = {"message": resp.text}
            raise APIError(resp.status_code, data)

        if resp.content:
            return resp.json()
        return {}

    # ---------------------------------------------------------------------
    # Public API – Contacts
    # ---------------------------------------------------------------------
    def test_api_key(self) -> Dict[str, Any]:
        return self._make_query(path="v1/api-key")

    def create_contact(
        self,
        email: str,
        properties: Optional[Dict[str, Union[str, int, bool, None]]] = None,
        mailing_lists: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        _validate_email(email)
        payload = {"email": email, **(properties or {}), "mailingLists": mailing_lists}
        return self._make_query(path="v1/contacts/create", method="POST", payload=payload)

    def update_contact(
        self,
        email: str,
        properties: Dict[str, Union[str, int, bool, None]],
        mailing_lists: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        _validate_email(email)
        payload = {"email": email, **properties, "mailingLists": mailing_lists}
        return self._make_query(path="v1/contacts/update", method="PUT", payload=payload)

    def find_contact(self, *, email: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if email and user_id:
            raise ValidationError("Only one of 'email' or 'user_id' may be provided.")
        if not email and not user_id:
            raise ValidationError("You must provide either 'email' or 'user_id'.")
        params: Dict[str, str] = {}
        if email:
            params["email"] = email
        if user_id:
            params["userId"] = user_id
        return self._make_query(path="v1/contacts/find", params=params)

    def delete_contact(self, *, email: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        if email and user_id:
            raise ValidationError("Only one of 'email' or 'user_id' may be provided.")
        if not email and not user_id:
            raise ValidationError("You must provide either 'email' or 'user_id'.")
        payload: Dict[str, str] = {}
        if email:
            payload["email"] = email
        if user_id:
            payload["userId"] = user_id
        return self._make_query(path="v1/contacts/delete", method="POST", payload=payload)

    # ------------------------------------------------------------------
    # Contact properties & mailing lists
    # ------------------------------------------------------------------
    def create_contact_property(self, name: str, type: str) -> Dict[str, Any]:  # noqa: A002 (shadow builtin)
        if type not in {"string", "number", "boolean", "date"}:
            raise ValidationError("type must be one of 'string', 'number', 'boolean', 'date'.")
        return self._make_query(
            path="v1/contacts/properties",
            method="POST",
            payload={"name": name, "type": type},
        )

    def get_custom_properties(self, list: str = "all") -> List[Dict[str, Any]]:  # noqa: A002
        if list not in {"all", "custom"}:
            raise ValidationError("list must be 'all' or 'custom'.")
        return self._make_query(path="v1/contacts/properties", params={"list": list})

    def get_mailing_lists(self) -> List[Dict[str, Any]]:
        return self._make_query(path="v1/lists")

    # ------------------------------------------------------------------
    # Events & transactional emails
    # ------------------------------------------------------------------
    def send_event(
        self,
        *,
        event_name: str,
        email: Optional[str] = None,
        user_id: Optional[str] = None,
        contact_properties: Optional[Dict[str, Union[str, int, bool, None]]] = None,
        event_properties: Optional[Dict[str, Union[str, int, bool]]] = None,
        mailing_lists: Optional[Dict[str, bool]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        if not email and not user_id:
            raise ValidationError("You must provide either 'email' or 'user_id'.")
        payload: Dict[str, Any] = {
            "eventName": event_name,
            **(contact_properties or {}),
            "eventProperties": event_properties,
            "mailingLists": mailing_lists,
        }
        if email:
            payload["email"] = email
        if user_id:
            payload["userId"] = user_id
        return self._make_query(path="v1/events/send", method="POST", headers=headers, payload=payload)

    def send_transactional_email(
        self,
        email: LoopsEmail,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send a transactional email.

        This method supports two calling styles:
        Pass a ``LoopsEmail`` instance as the first positional argument.
        """

        payload = email.to_dict()

        return self._make_query(path="v1/transactional", method="POST", headers=headers, payload=payload)

    def get_transactional_emails(
        self,
        *,
        per_page: int = 20,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not 10 <= per_page <= 50:
            raise ValidationError("per_page must be between 10 and 50.")
        params: Dict[str, str] = {"perPage": str(per_page)}
        if cursor:
            params["cursor"] = cursor
        return self._make_query(path="v1/transactional", params=params)


# ---------------------------------------------------------------------------
# Public re-exports
# ---------------------------------------------------------------------------
__all__: list[str] = [
    # Core client & errors
    "LoopsClient",
    "LoopsEmail",
    "Attachment",
    "RateLimitExceededError",
    "APIError",
    "ValidationError",
]
