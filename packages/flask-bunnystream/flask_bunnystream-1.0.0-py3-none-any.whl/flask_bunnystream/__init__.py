try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("bunnystream")
except ImportError:
    # Python < 3.8
    try:
        from importlib_metadata import PackageNotFoundError, version  # type: ignore

        __version__ = version("bunnystream")
    except ImportError:
        __version__ = "0.0.1-dev"
except (PackageNotFoundError, Exception):  # pylint: disable=broad-exception-caught
    # Fallback for development mode or package not installed
    __version__ = "0.0.1-dev"

from .extension import BunnyStream, BunnyStreamConfigError, get_bunnystream

# Alias for backward compatibility and clearer naming
BunnyStreamExtension = BunnyStream
from .decorators import (
    event_handler,
    user_event,
    order_event,
    system_event,
    register_pending_handlers,
)

__all__ = [
    "BunnyStream",
    "BunnyStreamExtension",
    "BunnyStreamConfigError",
    "get_bunnystream",
    "event_handler",
    "user_event",
    "order_event",
    "system_event",
    "register_pending_handlers",
]
