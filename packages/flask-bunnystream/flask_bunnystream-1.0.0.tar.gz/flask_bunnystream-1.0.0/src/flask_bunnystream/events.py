"""
This module provides event classes for integrating BunnyStream event tracking within a
Flask application.

It defines a `FlaskBaseEvent` class that extends the base event functionality from the
`bunnystream` package, adding Flask-specific context such as client IP address, browser,
and operating system information. The event metadata is automatically enriched with
client data extracted from the Flask request context, facilitating detailed event
logging and analytics.

Classes:
    FlaskBaseEvent: Base class for BunnyStream events in a Flask context, with automatic
                    client metadata enrichment.

"""

from typing import Any, Optional, Dict
from bunnystream.events import BaseEvent
from flask import current_app, request
from user_agents import parse


class FlaskBaseEvent(BaseEvent):
    """Base class for Flask BunnyStream events."""

    def __init__(self, **kwargs):
        warren = current_app.extensions.get("flask-bunnystream", None)
        super().__init__(warren, **kwargs)

    def set_metadata(self) -> None:
        """
        Sets metadata for the current object by invoking the superclass's set_metadata method,
        retrieving client-specific data, and storing it under the '_meta_' key with the
        subkey 'client_data'.

        This method updates the object's metadata dictionary to include additional
        client-related information.
        """
        super().set_metadata()
        client_data = self._get_client_data()
        self["_meta_"]["client_data"] = client_data  # type: ignore[attr-defined]

    def _get_client_ip(self) -> Optional[str]:
        """Get the client IP address from the Flask request context."""
        try:
            x_forwarded_for = request.headers.get("X-Forwarded-For", None)
            if x_forwarded_for:
                # Take the first IP in the list
                ip_address = x_forwarded_for.split(",")[0].strip()
            else:
                ip_address = request.remote_addr
        except RuntimeError:
            ip_address = None

        return ip_address

    def _get_client_data(self) -> Dict[str, Any]:
        user_agent = parse(request.user_agent.string)
        return {
            "ip_address": self._get_client_ip(),
            "browser": {
                "name": user_agent.browser.family,
                "version": user_agent.browser.version[0] if user_agent.browser.version else None,
            },
            "os": user_agent.os.family,
            "mobile": user_agent.is_mobile,
        }
