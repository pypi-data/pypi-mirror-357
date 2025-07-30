"""
Integration test for the Flask-BunnyStream example application.
Tests the actual integration with the flask-bunnystream extension.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from flask import Flask
from flask_bunnystream import BunnyStreamExtension
from bunnystream.events import BaseEvent


class TestEvent(BaseEvent):
    """Test event for integration testing."""

    def __init__(self, test_data: str):
        # Mock warren parameter since we're testing without a real BunnyStream instance
        super().__init__(warren=Mock())
        self.test_data = test_data


def test_extension_integration():
    """Test that the BunnyStreamExtension integrates correctly with Flask."""

    app = Flask(__name__)
    app.config["BUNNYSTREAM_URL"] = "amqp://test:test@localhost:5672/"
    app.config["BUNNYSTREAM_EXCHANGE"] = "test_exchange"
    app.config["BUNNYSTREAM_QUEUE"] = "test_queue"

    # Initialize extension
    bunnystream_ext = BunnyStreamExtension()

    # Test lazy initialization
    assert bunnystream_ext.bunnystream is None

    # Initialize with app
    with patch("bunnystream.BunnyStream") as mock_bunnystream:
        bunnystream_ext.init_app(app)

        # Test that BunnyStream was initialized with correct parameters
        mock_bunnystream.assert_called_once_with(
            url="amqp://test:test@localhost:5672/", exchange="test_exchange", queue="test_queue"
        )

        # Test that the extension is accessible
        assert bunnystream_ext.bunnystream is not None


def test_example_app_structure():
    """Test that the example app has the expected structure."""

    # Import the app module
    from app import create_app, ReceivedEvent, UserCreatedEvent, OrderPlacedEvent

    # Test app creation
    app = create_app()
    assert isinstance(app, Flask)

    # Test that configuration is set
    assert "BUNNYSTREAM_URL" in app.config
    assert "BUNNYSTREAM_EXCHANGE" in app.config
    assert "BUNNYSTREAM_QUEUE" in app.config

    # Test event classes exist
    assert UserCreatedEvent
    assert OrderPlacedEvent

    # Test database model exists
    assert ReceivedEvent


def test_event_creation():
    """Test that custom events can be created."""

    from app import UserCreatedEvent, OrderPlacedEvent

    # Mock warren for testing
    with patch("bunnystream.events.BaseEvent.__init__") as mock_init:
        mock_init.return_value = None

        # Test UserCreatedEvent
        user_event = UserCreatedEvent(user_id=123, username="test_user", email="test@example.com")

        assert user_event.user_id == 123
        assert user_event.username == "test_user"
        assert user_event.email == "test@example.com"

        # Test OrderPlacedEvent
        order_event = OrderPlacedEvent(order_id=456, user_id=123, total_amount=99.99)

        assert order_event.order_id == 456
        assert order_event.user_id == 123
        assert order_event.total_amount == 99.99


def test_consumer_structure():
    """Test that the consumer has the expected structure."""

    from consumer import EventConsumer

    # Create a mock app
    app = Flask(__name__)
    app.config["BUNNYSTREAM_URL"] = "amqp://test:test@localhost:5672/"
    app.config["BUNNYSTREAM_EXCHANGE"] = "test_exchange"
    app.config["BUNNYSTREAM_QUEUE"] = "test_queue"

    # Test consumer creation
    consumer = EventConsumer(app)
    assert consumer.app == app
    assert consumer.bunnystream is None
    assert consumer.running is False


def test_flask_routes_exist():
    """Test that the Flask app has the expected routes."""

    from app import create_app

    app = create_app()

    # Test that routes are registered
    routes = [rule.rule for rule in app.url_map.iter_rules()]

    expected_routes = [
        "/",
        "/health",
        "/api/events/user",
        "/api/events/order",
        "/api/events",
        "/api/events/<int:event_id>/processed",
    ]

    for route in expected_routes:
        assert any(route in r for r in routes), f"Route {route} not found"


def test_database_model():
    """Test the ReceivedEvent database model."""

    from app import ReceivedEvent

    # Test model attributes
    assert hasattr(ReceivedEvent, "id")
    assert hasattr(ReceivedEvent, "event_type")
    assert hasattr(ReceivedEvent, "event_data")
    assert hasattr(ReceivedEvent, "received_at")
    assert hasattr(ReceivedEvent, "processed")
    assert hasattr(ReceivedEvent, "to_dict")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
