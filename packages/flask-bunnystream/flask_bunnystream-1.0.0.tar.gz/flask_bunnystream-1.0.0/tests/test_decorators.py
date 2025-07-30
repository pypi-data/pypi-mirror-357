"""Tests for Flask-BunnyStream decorators."""

from unittest.mock import Mock, patch
from flask import Flask

from flask_bunnystream.decorators import (
    event_handler,
    user_event,
    order_event,
    system_event,
    register_pending_handlers,
    get_event_handlers,
    get_all_event_handlers,
    trigger_event_handlers,
    _global_event_handlers,
)
from flask_bunnystream import BunnyStream


class TestEventHandlerDecorator:
    """Test suite for the event_handler decorator."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear global handlers before each test
        _global_event_handlers.clear()

    def test_event_handler_decorator_basic(self):
        """Test basic event handler decorator functionality."""

        @event_handler("user.created")
        def handle_user_created(event_data):
            return f"Handled: {event_data}"

        # Check that metadata is stored
        assert hasattr(handle_user_created, "event_name")
        assert hasattr(handle_user_created, "queue_name")
        assert hasattr(handle_user_created, "is_event_handler")

        assert handle_user_created.event_name == "user.created"
        assert handle_user_created.queue_name == "handle_user_created_queue"
        assert handle_user_created.is_event_handler is True

    def test_event_handler_with_custom_queue_name(self):
        """Test event handler with custom queue name."""

        @event_handler("order.completed", queue_name="custom_order_queue")
        def handle_order_completed(event_data):
            return f"Order completed: {event_data}"

        assert handle_order_completed.event_name == "order.completed"
        assert handle_order_completed.queue_name == "custom_order_queue"

    def test_event_handler_function_still_callable(self):
        """Test that decorated function is still callable."""

        @event_handler("test.event")
        def test_handler(event_data):
            return f"Processed: {event_data}"

        result = test_handler("test data")
        assert result == "Processed: test data"

    def test_event_handler_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""

        @event_handler("test.event")
        def test_handler(event_data):
            """Test handler function."""
            return event_data

        assert test_handler.__name__ == "test_handler"
        assert test_handler.__doc__ == "Test handler function."

    def test_event_handler_registration_outside_app_context(self):
        """Test event handler registration outside Flask app context."""

        @event_handler("global.event")
        def global_handler(event_data):
            return event_data

        # Should be stored in global registry
        assert "global.event" in _global_event_handlers
        assert global_handler in _global_event_handlers["global.event"]

    def test_event_handler_registration_with_app_context(self):
        """Test event handler registration within Flask app context."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch("flask_bunnystream.extension.Warren"):
            bunnystream = BunnyStream(app)

            with app.app_context():

                @event_handler("app.event")
                def app_handler(event_data):
                    return event_data

                # Should be registered with the app
                handlers = get_event_handlers(app, "app.event")
                assert app_handler in handlers

    def test_event_handler_registration_when_bunnystream_not_initialized(self):
        """Test event handler registration when BunnyStream is not initialized."""
        app = Flask(__name__)

        with app.app_context():

            @event_handler("pending.event")
            def pending_handler(event_data):
                return event_data

            # Should be stored in global registry for later registration
            assert "pending.event" in _global_event_handlers

    def test_register_pending_handlers(self):
        """Test registration of pending handlers."""
        app = Flask(__name__)

        # Create some pending handlers
        @event_handler("pending1")
        def handler1(event_data):
            return event_data

        @event_handler("pending2")
        def handler2(event_data):
            return event_data

        # Handlers should be in global registry
        assert "pending1" in _global_event_handlers
        assert "pending2" in _global_event_handlers

        # Register pending handlers
        register_pending_handlers(app)

        # Handlers should now be registered with the app
        assert get_event_handlers(app, "pending1") == [handler1]
        assert get_event_handlers(app, "pending2") == [handler2]

        # Global registry should be cleared
        assert len(_global_event_handlers) == 0

    def test_get_event_handlers_empty(self):
        """Test getting handlers when none are registered."""
        app = Flask(__name__)
        handlers = get_event_handlers(app, "nonexistent.event")
        assert handlers == []

    def test_get_all_event_handlers_empty(self):
        """Test getting all handlers when none are registered."""
        app = Flask(__name__)
        handlers = get_all_event_handlers(app)
        assert handlers == {}

    def test_get_all_event_handlers_with_data(self):
        """Test getting all handlers when some are registered."""
        app = Flask(__name__)

        @event_handler("event1")
        def handler1(event_data):
            return event_data

        @event_handler("event2")
        def handler2(event_data):
            return event_data

        register_pending_handlers(app)

        all_handlers = get_all_event_handlers(app)
        assert "event1" in all_handlers
        assert "event2" in all_handlers
        assert handler1 in all_handlers["event1"]
        assert handler2 in all_handlers["event2"]

    def test_trigger_event_handlers(self):
        """Test triggering event handlers."""
        app = Flask(__name__)

        # Mock handler
        mock_handler = Mock()
        mock_handler.__name__ = "mock_handler"

        # Register handler manually
        setattr(app, "bunnystream_event_handlers", {"test.event": [mock_handler]})

        # Trigger handlers
        trigger_event_handlers(app, "test.event", {"data": "test"})

        # Verify handler was called
        mock_handler.assert_called_once_with({"data": "test"})

    def test_trigger_event_handlers_with_error(self):
        """Test triggering event handlers when handler raises error."""
        app = Flask(__name__)

        # Create handler that raises an error
        def error_handler(event_data):
            raise ValueError("Handler error")

        error_handler.__name__ = "error_handler"

        # Register handler manually
        setattr(app, "bunnystream_event_handlers", {"error.event": [error_handler]})

        # Mock logger
        app.logger = Mock()

        # Trigger handlers - should not raise exception
        trigger_event_handlers(app, "error.event", {"data": "test"})

        # Verify error was logged
        app.logger.error.assert_called_once()
        assert "error_handler" in str(app.logger.error.call_args)

    def test_multiple_handlers_same_event(self):
        """Test multiple handlers for the same event."""
        app = Flask(__name__)

        @event_handler("multi.event")
        def handler1(event_data):
            return f"Handler1: {event_data}"

        @event_handler("multi.event")
        def handler2(event_data):
            return f"Handler2: {event_data}"

        register_pending_handlers(app)

        handlers = get_event_handlers(app, "multi.event")
        assert len(handlers) == 2
        assert handler1 in handlers
        assert handler2 in handlers


class TestSpecializedDecorators:
    """Test suite for specialized event decorators."""

    def setup_method(self):
        """Set up test fixtures."""
        _global_event_handlers.clear()

    def test_user_event_decorator(self):
        """Test user_event decorator."""

        @user_event("created")
        def handle_user_created(event_data):
            return event_data

        assert handle_user_created.event_name == "user.created"
        assert handle_user_created.queue_name == "handle_user_created_queue"

    def test_user_event_with_custom_queue(self):
        """Test user_event decorator with custom queue."""

        @user_event("updated", queue_name="user_updates")
        def handle_user_updated(event_data):
            return event_data

        assert handle_user_updated.event_name == "user.updated"
        assert handle_user_updated.queue_name == "user_updates"

    def test_order_event_decorator(self):
        """Test order_event decorator."""

        @order_event("completed")
        def handle_order_completed(event_data):
            return event_data

        assert handle_order_completed.event_name == "order.completed"
        assert handle_order_completed.queue_name == "handle_order_completed_queue"

    def test_system_event_decorator(self):
        """Test system_event decorator."""

        @system_event("startup")
        def handle_system_startup(event_data):
            return event_data

        assert handle_system_startup.event_name == "system.startup"
        assert handle_system_startup.queue_name == "handle_system_startup_queue"

    def test_specialized_decorators_register_correctly(self):
        """Test that specialized decorators register handlers correctly."""
        app = Flask(__name__)

        @user_event("created")
        def user_handler(event_data):
            return event_data

        @order_event("completed")
        def order_handler(event_data):
            return event_data

        @system_event("startup")
        def system_handler(event_data):
            return event_data

        register_pending_handlers(app)

        assert get_event_handlers(app, "user.created") == [user_handler]
        assert get_event_handlers(app, "order.completed") == [order_handler]
        assert get_event_handlers(app, "system.startup") == [system_handler]


class TestIntegrationWithBunnyStream:
    """Test integration with BunnyStream extension."""

    def test_handlers_work_with_bunnystream_extension(self):
        """Test that event handlers work with BunnyStream extension."""
        app = Flask(__name__)
        app.config["BUNNYSTREAM_MODE"] = "producer"

        with patch("flask_bunnystream.extension.Warren"):
            bunnystream = BunnyStream(app)

            @event_handler("integration.test")
            def integration_handler(event_data):
                return f"Integrated: {event_data}"

            register_pending_handlers(app)

            # Verify handler is registered
            handlers = get_event_handlers(app, "integration.test")
            assert integration_handler in handlers

            # Verify BunnyStream is initialized
            assert bunnystream.is_initialized
