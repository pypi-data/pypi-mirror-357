"""
Comprehensive tests for the FlaskBaseEvent class.
"""

import pytest
from unittest.mock import Mock, patch
from flask import Flask

from flask_bunnystream.events import FlaskBaseEvent


class TestFlaskBaseEvent:
    """Test suite for FlaskBaseEvent class."""

    @pytest.fixture
    def app(self):
        """Create a Flask test application."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["BUNNYSTREAM_RABBITMQ_URL"] = "amqp://test-localhost"
        app.config["BUNNYSTREAM_MODE"] = "consumer"
        return app

    def test_inheritance_from_base_event(self):
        """Test that FlaskBaseEvent properly inherits from BaseEvent."""
        from bunnystream.events import BaseEvent

        assert issubclass(FlaskBaseEvent, BaseEvent)

    def test_init_with_flask_extension(self, app):
        """Test FlaskBaseEvent initialization with Flask extension."""
        with app.app_context():
            # Mock the extensions
            mock_warren = Mock()
            app.extensions = {"flask-bunnystream": mock_warren}

            with patch("flask_bunnystream.events.BaseEvent.__init__") as mock_base_init:
                event = FlaskBaseEvent(test_param="test_value")

                # Verify BaseEvent.__init__ was called correctly
                mock_base_init.assert_called_once_with(mock_warren, test_param="test_value")

    def test_init_without_flask_extension(self, app):
        """Test FlaskBaseEvent initialization when flask-bunnystream extension is not found."""
        with app.app_context():
            # Ensure no extension is present
            app.extensions = {}

            with patch("flask_bunnystream.events.BaseEvent.__init__") as mock_base_init:
                event = FlaskBaseEvent()

                # Verify BaseEvent.__init__ was called with None as warren
                mock_base_init.assert_called_once_with(None)

    def test_get_client_ip_with_x_forwarded_for(self, app):
        """Test _get_client_ip with X-Forwarded-For header."""
        with app.test_request_context(
            "/",
            headers={"X-Forwarded-For": "192.168.1.100, 10.0.0.1"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    ip = event._get_client_ip()
                    assert ip == "192.168.1.100"

    def test_get_client_ip_with_x_forwarded_for_single_ip(self, app):
        """Test _get_client_ip with single IP in X-Forwarded-For header."""
        with app.test_request_context(
            "/",
            headers={"X-Forwarded-For": "203.0.113.195"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    ip = event._get_client_ip()
                    assert ip == "203.0.113.195"

    def test_get_client_ip_without_x_forwarded_for(self, app):
        """Test _get_client_ip without X-Forwarded-For header."""
        with app.test_request_context("/", environ_base={"REMOTE_ADDR": "203.0.113.195"}):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    ip = event._get_client_ip()
                    assert ip == "203.0.113.195"

    def test_get_client_ip_with_whitespace_in_forwarded_for(self, app):
        """Test _get_client_ip strips whitespace from X-Forwarded-For header."""
        with app.test_request_context(
            "/",
            headers={"X-Forwarded-For": " 192.168.1.100 , 10.0.0.1 "},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    ip = event._get_client_ip()
                    assert ip == "192.168.1.100"

    def test_get_client_data_chrome_browser(self, app):
        """Test _get_client_data correctly parses Chrome browser."""
        chrome_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        with app.test_request_context(
            "/", headers={"User-Agent": chrome_ua}, environ_base={"REMOTE_ADDR": "127.0.0.1"}
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    client_data = event._get_client_data()

                    assert client_data["browser"]["name"] == "Chrome"
                    assert client_data["browser"]["version"] == 91
                    assert client_data["os"] == "Windows"
                    assert client_data["mobile"] is False

    def test_get_client_data_firefox_browser(self, app):
        """Test _get_client_data correctly parses Firefox browser."""
        firefox_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        )

        with app.test_request_context(
            "/", headers={"User-Agent": firefox_ua}, environ_base={"REMOTE_ADDR": "127.0.0.1"}
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    client_data = event._get_client_data()

                    assert client_data["browser"]["name"] == "Firefox"
                    assert client_data["browser"]["version"] == 89
                    assert client_data["os"] == "Windows"
                    assert client_data["mobile"] is False

    def test_get_client_data_mobile_browser(self, app):
        """Test _get_client_data correctly identifies mobile browser."""
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"

        with app.test_request_context(
            "/", headers={"User-Agent": mobile_ua}, environ_base={"REMOTE_ADDR": "127.0.0.1"}
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    client_data = event._get_client_data()

                    assert client_data["browser"]["name"] == "Mobile Safari"
                    assert client_data["os"] == "iOS"
                    assert client_data["mobile"] is True

    def test_get_client_data_complete_structure(self, app):
        """Test _get_client_data returns complete client information structure."""
        with app.test_request_context(
            "/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "X-Forwarded-For": "192.168.1.100",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    client_data = event._get_client_data()

                    # Verify structure
                    assert isinstance(client_data, dict)
                    assert "ip_address" in client_data
                    assert "browser" in client_data
                    assert "os" in client_data
                    assert "mobile" in client_data

                    # Verify types and values
                    assert client_data["ip_address"] == "192.168.1.100"
                    assert isinstance(client_data["browser"], dict)
                    assert "name" in client_data["browser"]
                    assert "version" in client_data["browser"]
                    assert isinstance(client_data["mobile"], bool)

    def test_get_client_data_with_no_ip(self, app):
        """Test _get_client_data when IP address is None."""
        with app.test_request_context(
            "/",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()

                    with patch.object(event, "_get_client_ip", return_value=None):
                        client_data = event._get_client_data()

                        assert client_data["ip_address"] is None
                        assert "browser" in client_data
                        assert "os" in client_data
                        assert "mobile" in client_data

    def test_get_client_data_outside_request_context(self, app):
        """Test _get_client_data behavior outside request context."""
        with app.app_context():
            app.extensions = {"flask-bunnystream": Mock()}
            with patch("flask_bunnystream.events.BaseEvent.__init__"):
                event = FlaskBaseEvent()

                # This should raise an error since we're outside request context
                with pytest.raises(RuntimeError):
                    event._get_client_data()

    def test_get_client_data_no_browser_version(self, app):
        """Test _get_client_data handles missing browser version."""
        minimal_ua = "CustomBot/1.0"

        with app.test_request_context(
            "/", headers={"User-Agent": minimal_ua}, environ_base={"REMOTE_ADDR": "127.0.0.1"}
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    client_data = event._get_client_data()

                    # Should handle missing version gracefully
                    assert "browser" in client_data
                    assert "version" in client_data["browser"]
                    # Version might be None for unknown browsers
                    assert client_data["browser"]["version"] is None or isinstance(
                        client_data["browser"]["version"], int
                    )

    def test_error_handling_in_get_client_data(self, app):
        """Test error handling in _get_client_data method."""
        with app.test_request_context("/"):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()

                    # Test with request that might cause parsing errors
                    with patch("flask_bunnystream.events.parse") as mock_parse:
                        mock_parse.side_effect = Exception("Parse error")

                        with pytest.raises(Exception):
                            event._get_client_data()

    @patch("flask_bunnystream.events.BaseEvent.set_metadata")
    def test_set_metadata_calls_parent_and_adds_client_data(self, mock_parent_set_metadata, app):
        """Test that set_metadata calls parent method and adds client data."""
        with app.test_request_context(
            "/",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}

                # Create a more realistic mock that simulates BaseEvent behavior
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()

                    # Mock the event data attribute that BaseEvent uses
                    event.data = {"_meta_": {"existing_meta": "value"}}

                    # Mock client data for predictable testing
                    mock_client_data = {
                        "ip_address": "127.0.0.1",
                        "browser": {"name": "Chrome", "version": 91},
                        "os": "Windows",
                        "mobile": False,
                    }

                    with patch.object(event, "_get_client_data", return_value=mock_client_data):
                        event.set_metadata()

                        # Verify parent method was called
                        mock_parent_set_metadata.assert_called_once()

                        # Verify client data was added to metadata
                        assert "client_data" in event.data["_meta_"]
                        assert event.data["_meta_"]["client_data"] == mock_client_data

    def test_mocked_request_parsing(self, app):
        """Test _get_client_data with mocked request object."""
        with app.test_request_context(
            "/",
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            environ_base={"REMOTE_ADDR": "10.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}
                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()
                    client_data = event._get_client_data()

                    assert client_data["ip_address"] == "10.0.0.1"
                    assert "browser" in client_data
                    assert "os" in client_data
                    assert "mobile" in client_data

    def test_integration_full_workflow(self, app):
        """Integration test for the complete FlaskBaseEvent workflow."""
        with app.test_request_context(
            "/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "X-Forwarded-For": "203.0.113.195, 192.168.1.1",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        ):
            with app.app_context():
                app.extensions = {"flask-bunnystream": Mock()}

                with patch("flask_bunnystream.events.BaseEvent.__init__"):
                    event = FlaskBaseEvent()

                    # Test IP extraction
                    ip = event._get_client_ip()
                    assert ip == "203.0.113.195"

                    # Test client data extraction
                    client_data = event._get_client_data()
                    assert client_data["ip_address"] == "203.0.113.195"
                    assert client_data["browser"]["name"] == "Chrome"
                    assert client_data["os"] == "Windows"
                    assert client_data["mobile"] is False

                    # Test metadata integration
                    event.data = {"_meta_": {}}
                    with patch("flask_bunnystream.events.BaseEvent.set_metadata"):
                        event.set_metadata()
                        assert "client_data" in event.data["_meta_"]
                        assert event.data["_meta_"]["client_data"] == client_data
