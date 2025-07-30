"""Comprehensive tests for the refactored BunnyStream Flask extension."""

import pytest
from unittest.mock import Mock, patch
from flask import Flask
from bunnystream import BunnyStreamConfig

from flask_bunnystream import BunnyStream, BunnyStreamConfigError, get_bunnystream


class TestBunnyStreamExtension:
    """Test suite for the BunnyStream Flask extension."""

    def test_immediate_initialization_with_flask_config(self):
        """Test immediate initialization using Flask configuration."""
        app = Flask(__name__)
        app.config.update(
            {
                "BUNNYSTREAM_MODE": "producer",
                "BUNNYSTREAM_EXCHANGE": "test_exchange",
                "BUNNYSTREAM_HOST": "localhost",
                "BUNNYSTREAM_PORT": 5672,
                "BUNNYSTREAM_VHOST": "/",
                "BUNNYSTREAM_USER": "guest",
                "BUNNYSTREAM_PASSWORD": "guest",
            }
        )

        with patch("flask_bunnystream.extension.Warren") as mock_warren:
            bunnystream = BunnyStream(app)

            # Verify Warren was created with correct config
            assert mock_warren.called
            assert bunnystream.is_initialized
            assert "flask-bunnystream" in app.extensions
            assert app.extensions["flask-bunnystream"] is bunnystream

    def test_immediate_initialization_with_explicit_config(self):
        """Test immediate initialization with explicit BunnyStreamConfig."""
        app = Flask(__name__)
        config = BunnyStreamConfig(mode="producer")

        with patch("flask_bunnystream.extension.Warren") as mock_warren:
            bunnystream = BunnyStream(app, config)

            mock_warren.assert_called_once_with(config)
            assert bunnystream.is_initialized
            assert bunnystream._config is config

    def test_lazy_initialization(self):
        """Test lazy initialization pattern."""
        bunnystream = BunnyStream()
        assert not bunnystream.is_initialized
        assert bunnystream.warren is None

        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "consumer"

        with patch("flask_bunnystream.extension.Warren") as mock_warren:
            bunnystream.init_app(app)

            assert mock_warren.called
            assert bunnystream.is_initialized
            assert "flask-bunnystream" in app.extensions

    def test_lazy_initialization_with_explicit_config(self):
        """Test lazy initialization with explicit config."""
        bunnystream = BunnyStream()
        app = Flask(__name__)
        config = BunnyStreamConfig(mode="consumer")

        with patch("flask_bunnystream.extension.Warren") as mock_warren:
            bunnystream.init_app(app, config)

            mock_warren.assert_called_once_with(config)
            assert bunnystream._config is config

    def test_missing_required_config(self):
        """Test error handling when required config is missing."""
        app = Flask(__name__)
        # No BUNNYSTREAM_MODE configured

        with pytest.raises(
            BunnyStreamConfigError, match="BUNNYSTREAM_MODE configuration is required"
        ):
            BunnyStream(app)

    def test_invalid_bunnystream_config(self):
        """Test error handling for invalid BunnyStreamConfig."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "invalid_mode"

        with pytest.raises(BunnyStreamConfigError, match="Invalid BunnyStream configuration"):
            BunnyStream(app)

    def test_warren_initialization_failure(self):
        """Test error handling when Warren initialization fails."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch(
            "flask_bunnystream.extension.Warren", side_effect=Exception("Connection failed")
        ):
            with pytest.raises(
                BunnyStreamConfigError, match="Failed to initialize BunnyStream Warren"
            ):
                BunnyStream(app)

    def test_get_warren_success(self):
        """Test getting Warren instance when properly initialized."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch("flask_bunnystream.extension.Warren") as mock_warren_class:
            mock_warren_instance = Mock()
            mock_warren_class.return_value = mock_warren_instance

            bunnystream = BunnyStream(app)
            warren = bunnystream.get_warren()

            assert warren is mock_warren_instance

    def test_get_warren_not_initialized(self):
        """Test getting Warren when not initialized raises error."""
        bunnystream = BunnyStream()

        with pytest.raises(RuntimeError, match="BunnyStream extension is not initialized"):
            bunnystream.get_warren()

    def test_publish_method_delegation(self):
        """Test that publish method delegates to Warren."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch("flask_bunnystream.extension.Warren") as mock_warren_class:
            mock_warren_instance = Mock()
            mock_warren_class.return_value = mock_warren_instance

            bunnystream = BunnyStream(app)
            bunnystream.publish("test.topic", {"message": "hello"})

            mock_warren_instance.publish.assert_called_once_with("test.topic", {"message": "hello"})

    def test_publish_not_initialized(self):
        """Test publish when not initialized raises error."""
        bunnystream = BunnyStream()

        with pytest.raises(RuntimeError, match="BunnyStream extension is not initialized"):
            bunnystream.publish("test.topic", {})

    def test_config_extraction_from_flask(self):
        """Test configuration extraction from Flask app config."""
        app = Flask(__name__)
        app.config.update(
            {
                "BUNNYSTREAM_MODE": "producer",
                "BUNNYSTREAM_EXCHANGE": "test_exchange",
                "BUNNYSTREAM_HOST": "example.com",
                "BUNNYSTREAM_PORT": 5673,
                "BUNNYSTREAM_VHOST": "/test",
                "BUNNYSTREAM_USER": "testuser",
                "BUNNYSTREAM_PASSWORD": "testpass",
            }
        )

        with (
            patch("flask_bunnystream.extension.Warren"),
            patch("flask_bunnystream.extension.BunnyStreamConfig") as mock_config_class,
        ):

            BunnyStream(app)

            # Verify BunnyStreamConfig was called with correct parameters
            mock_config_class.assert_called_once_with(
                mode="producer",
                exchange_name="test_exchange",
                rabbit_host="example.com",
                rabbit_port=5673,
                rabbit_vhost="/test",
                rabbit_user="testuser",
                rabbit_pass="testpass",
            )

    def test_config_extraction_with_none_values(self):
        """Test that None values are filtered out from config."""
        app = Flask(__name__)
        app.config.update(
            {
                "BUNNYSTREAM_MODE": "consumer",
                "BUNNYSTREAM_EXCHANGE": "test_exchange",
                # Other values not set (will be None)
            }
        )

        with (
            patch("flask_bunnystream.extension.Warren"),
            patch("flask_bunnystream.extension.BunnyStreamConfig") as mock_config_class,
        ):

            BunnyStream(app)

            # Verify only non-None values were passed
            mock_config_class.assert_called_once_with(
                mode="consumer", exchange_name="test_exchange"
            )

    def test_multiple_app_initialization(self):
        """Test that extension can be used with multiple apps."""
        bunnystream = BunnyStream()

        app1 = Flask("app1")
        app1.config["BUNNYSTREAM_MODE"] = "producer"

        app2 = Flask("app2")
        app2.config["BUNNYSTREAM_MODE"] = "consumer"

        with patch("flask_bunnystream.extension.Warren"):
            bunnystream.init_app(app1)
            bunnystream.init_app(app2)

            assert "flask-bunnystream" in app1.extensions
            assert "flask-bunnystream" in app2.extensions
            assert app1.extensions["flask-bunnystream"] is bunnystream
            assert app2.extensions["flask-bunnystream"] is bunnystream

    def test_get_bunnystream_from_context(self):
        """Test getting BunnyStream from Flask application context."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch("flask_bunnystream.extension.Warren"):
            bunnystream = BunnyStream(app)

            with app.app_context():
                retrieved = get_bunnystream()
                assert retrieved is bunnystream

    def test_get_bunnystream_not_initialized(self):
        """Test get_bunnystream when extension is not initialized."""
        app = Flask(__name__)

        with app.app_context():
            with pytest.raises(RuntimeError, match="BunnyStream extension is not initialized"):
                get_bunnystream()

    def test_get_bunnystream_no_extensions(self):
        """Test get_bunnystream when app has no extensions attribute."""
        app = Flask(__name__)

        # Remove extensions attribute if it exists
        if hasattr(app, "extensions"):
            delattr(app, "extensions")

        with app.app_context():
            with pytest.raises(RuntimeError, match="BunnyStream extension is not initialized"):
                get_bunnystream()

    def test_teardown_handler_registration(self):
        """Test that teardown handler is properly registered."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch("flask_bunnystream.extension.Warren"):
            bunnystream = BunnyStream(app)

            # Verify teardown handler was registered
            teardown_handlers = app.teardown_appcontext_funcs
            assert any(handler.__name__ == "_teardown" for handler in teardown_handlers)

    def test_teardown_handler_execution(self):
        """Test that teardown handler can be called without error."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch("flask_bunnystream.extension.Warren"):
            bunnystream = BunnyStream(app)

            # Call teardown handler directly (it should not raise an error)
            bunnystream._teardown(None)
            bunnystream._teardown(Exception("test error"))
