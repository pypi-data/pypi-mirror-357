"""Flask-BunnyStream extension for integrating BunnyStream with Flask applications."""

from typing import Optional, Any
from flask import Flask, current_app
from bunnystream import Warren, BunnyStreamConfig


class BunnyStreamConfigError(Exception):
    """Raised when there's an error with BunnyStream configuration."""


class BunnyStream:
    """Flask extension for BunnyStream integration.

    This extension allows Flask applications to easily integrate with BunnyStream
    messaging service. It supports both immediate and lazy initialization patterns
    common in Flask applications.

    Example usage:
        # Immediate initialization
        app = Flask(__name__)
        app.config['BUNNYSTREAM_MODE'] = 'development'
        app.config['BUNNYSTREAM_EXCHANGE'] = 'my_exchange'
        bunnystream = BunnyStream(app)

        # Lazy initialization (application factory pattern)
        bunnystream = BunnyStream()

        def create_app():
            app = Flask(__name__)
            bunnystream.init_app(app)
            return app
    """

    def __init__(self, app: Optional[Flask] = None, config: Optional[BunnyStreamConfig] = None):
        """Initialize the BunnyStream extension.

        Args:
            app: Flask application instance (optional for lazy initialization)
            config: BunnyStreamConfig instance (optional, will be created from Flask config if not provided)
        """
        self.warren: Optional[Warren] = None
        self._config: Optional[BunnyStreamConfig] = config

        if app is not None:
            self.init_app(app, config)

    def init_app(self, app: Flask, config: Optional[BunnyStreamConfig] = None) -> None:
        """Initialize the extension with a Flask application.

        This method can be called multiple times to initialize the extension
        with different Flask applications (useful for testing or multi-app setups).

        Args:
            app: Flask application instance
            config: BunnyStreamConfig instance (optional, will be created from Flask config if not provided)

        Raises:
            BunnyStreamConfigError: If configuration is invalid or missing required parameters
        """
        if config is not None:
            self._config = config
        elif self._config is None:
            # Extract configuration from Flask app config
            self._config = self._create_config_from_app(app)

        try:
            self.warren = Warren(self._config)
        except Exception as e:
            raise BunnyStreamConfigError(f"Failed to initialize BunnyStream Warren: {e}") from e

        # Store extension in app extensions
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["flask-bunnystream"] = self

        # Add teardown handler to clean up resources
        app.teardown_appcontext(self._teardown)

    def _create_config_from_app(self, app: Flask) -> BunnyStreamConfig:
        """Create BunnyStreamConfig from Flask application configuration.

        Args:
            app: Flask application instance

        Returns:
            BunnyStreamConfig instance

        Raises:
            BunnyStreamConfigError: If required configuration is missing
        """
        # Extract configuration with defaults
        mode = app.config.get("BUNNYSTREAM_MODE")
        if not mode:
            raise BunnyStreamConfigError("BUNNYSTREAM_MODE configuration is required")

        config_kwargs = {
            "mode": mode,
            "exchange_name": app.config.get("BUNNYSTREAM_EXCHANGE"),
            "rabbit_host": app.config.get("BUNNYSTREAM_HOST"),
            "rabbit_port": app.config.get("BUNNYSTREAM_PORT"),
            "rabbit_vhost": app.config.get("BUNNYSTREAM_VHOST"),
            "rabbit_user": app.config.get("BUNNYSTREAM_USER"),
            "rabbit_pass": app.config.get("BUNNYSTREAM_PASSWORD"),
        }

        # Remove None values to let BunnyStreamConfig use its defaults
        config_kwargs = {k: v for k, v in config_kwargs.items() if v is not None}

        try:
            return BunnyStreamConfig(**config_kwargs)
        except Exception as e:
            raise BunnyStreamConfigError(f"Invalid BunnyStream configuration: {e}") from e

    def _teardown(self, exception: Optional[Exception]) -> None:
        """Clean up resources when application context is torn down.

        Args:
            exception: Exception that caused the teardown (if any)
        """
        # Placeholder for any cleanup operations
        # BunnyStream Warren doesn't currently require explicit cleanup,
        # but this is here for future extensibility

    @property
    def is_initialized(self) -> bool:
        """Check if the extension is properly initialized.

        Returns:
            True if warren is initialized, False otherwise
        """
        return self.warren is not None

    def get_warren(self) -> Warren:
        """Get the Warren instance.

        Returns:
            Warren instance

        Raises:
            RuntimeError: If the extension is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError(
                "BunnyStream extension is not initialized. "
                "Make sure to call init_app() with a Flask application."
            )
        assert self.warren is not None  # For type checker
        return self.warren

    def publish(self, *args, **kwargs) -> Any:
        """Publish a message using the Warren instance.

        This is a convenience method that delegates to warren.publish().

        Args:
            *args: Positional arguments to pass to warren.publish()
            **kwargs: Keyword arguments to pass to warren.publish()

        Returns:
            Whatever warren.publish() returns

        Raises:
            RuntimeError: If the extension is not initialized
        """
        return self.get_warren().publish(*args, **kwargs)


def get_bunnystream() -> BunnyStream:
    """Get the BunnyStream extension from the current Flask application context.

    Returns:
        BunnyStream extension instance

    Raises:
        RuntimeError: If no Flask application context is available or extension is not initialized
    """
    if not hasattr(current_app, "extensions") or "flask-bunnystream" not in current_app.extensions:
        raise RuntimeError(
            "BunnyStream extension is not initialized for this application. "
            "Make sure to initialize it with BunnyStream(app) or bunnystream.init_app(app)."
        )
    return current_app.extensions["flask-bunnystream"]  # type: ignore
