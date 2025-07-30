"""Decorators for Flask-BunnyStream extension."""

import functools
from typing import Callable, Any, Optional, Dict, List
from flask import current_app, has_app_context
from flask_bunnystream.extension import get_bunnystream


# Global registry for event handlers when no app context is available
_global_event_handlers: Dict[str, List[Callable]] = {}


def event_handler(event_name: str, queue_name: Optional[str] = None):
    """Decorator to register a function as an event handler.

    This decorator registers a function to handle specific events from BunnyStream.
    The decorated function will be called when the specified event is received.

    Args:
        event_name: The name of the event to handle (e.g., 'user.created', 'order.completed')
        queue_name: Optional queue name for the handler. If not provided,
                   a queue name will be generated based on the function name.

    Example:
        @event_handler('user.created')
        def handle_user_created(event_data):
            print(f"New user created: {event_data}")

        @event_handler('order.completed', queue_name='order_processing_queue')
        def handle_order_completion(event_data):
            # Process completed order
            send_confirmation_email(event_data['user_email'])

    Returns:
        The decorated function
    """

    def decorator(func: Callable) -> Callable:
        # Generate queue name if not provided
        actual_queue_name = queue_name or f"{func.__name__}_queue"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store event handler metadata using setattr to avoid type checker issues
        setattr(wrapper, "event_name", event_name)
        setattr(wrapper, "queue_name", actual_queue_name)
        setattr(wrapper, "is_event_handler", True)

        # Register the handler
        _register_event_handler(event_name, wrapper)

        return wrapper

    return decorator


def _register_event_handler(event_name: str, handler_func: Callable) -> None:
    """Register an event handler function.

    Args:
        event_name: The event name to register for
        handler_func: The handler function
    """
    if has_app_context():
        # We're in an app context, register with the current app
        try:
            get_bunnystream()  # Just check if it's available
            _register_handler_with_app(current_app, event_name, handler_func)
        except RuntimeError:
            # BunnyStream not initialized yet, store for later registration
            _store_handler_for_later_registration(event_name, handler_func)
    else:
        # No app context, store in global registry
        _store_handler_for_later_registration(event_name, handler_func)


def _register_handler_with_app(app, event_name: str, handler_func: Callable) -> None:
    """Register a handler with a specific Flask app.

    Args:
        app: Flask application instance
        event_name: The event name
        handler_func: The handler function
    """
    # Initialize event handlers registry in app if not exists
    handlers_attr = "bunnystream_event_handlers"
    if not hasattr(app, handlers_attr):
        setattr(app, handlers_attr, {})

    # Add handler to app registry
    handlers = getattr(app, handlers_attr)
    if event_name not in handlers:
        handlers[event_name] = []

    handlers[event_name].append(handler_func)

    # Log registration
    app.logger.info(f"Registered event handler '{handler_func.__name__}' for event '{event_name}'")


def _store_handler_for_later_registration(event_name: str, handler_func: Callable) -> None:
    """Store handler in global registry for later registration.

    Args:
        event_name: The event name
        handler_func: The handler function
    """
    if event_name not in _global_event_handlers:
        _global_event_handlers[event_name] = []

    _global_event_handlers[event_name].append(handler_func)


def register_pending_handlers(app) -> None:
    """Register all pending event handlers with a Flask app.

    This function should be called after BunnyStream is initialized to register
    any handlers that were decorated before the app context was available.

    Args:
        app: Flask application instance
    """
    for event_name, handlers in _global_event_handlers.items():
        for handler in handlers:
            _register_handler_with_app(app, event_name, handler)

    # Clear global registry after registration
    _global_event_handlers.clear()


def get_event_handlers(app, event_name: str) -> List[Callable]:
    """Get all registered handlers for a specific event.

    Args:
        app: Flask application instance
        event_name: The event name to get handlers for

    Returns:
        List of handler functions for the event
    """
    handlers_attr = "bunnystream_event_handlers"
    if not hasattr(app, handlers_attr):
        return []

    handlers = getattr(app, handlers_attr)
    return handlers.get(event_name, [])


def get_all_event_handlers(app) -> Dict[str, List[Callable]]:
    """Get all registered event handlers for an app.

    Args:
        app: Flask application instance

    Returns:
        Dictionary mapping event names to lists of handler functions
    """
    handlers_attr = "bunnystream_event_handlers"
    if not hasattr(app, handlers_attr):
        return {}

    handlers = getattr(app, handlers_attr)
    return handlers.copy()


def trigger_event_handlers(app, event_name: str, event_data: Any) -> None:
    """Trigger all registered handlers for a specific event.

    Args:
        app: Flask application instance
        event_name: The event name
        event_data: The event data to pass to handlers
    """
    handlers = get_event_handlers(app, event_name)

    for handler in handlers:
        try:
            with app.app_context():
                handler(event_data)
        except (ValueError, TypeError, RuntimeError) as e:
            app.logger.error(
                f"Error in event handler '{handler.__name__}' for event '{event_name}': {e}"
            )
        except Exception as e:  # pylint: disable=broad-except
            app.logger.error(
                f"Unexpected error in event handler '{handler.__name__}' for event '{event_name}': {e}"
            )


# Helper decorator for common event patterns
def user_event(action: str, queue_name: Optional[str] = None):
    """Decorator for user-related events.

    Args:
        action: The user action (e.g., 'created', 'updated', 'deleted')
        queue_name: Optional queue name

    Example:
        @user_event('created')
        def handle_user_created(event_data):
            send_welcome_email(event_data['email'])
    """
    return event_handler(f"user.{action}", queue_name)


def order_event(action: str, queue_name: Optional[str] = None):
    """Decorator for order-related events.

    Args:
        action: The order action (e.g., 'created', 'completed', 'cancelled')
        queue_name: Optional queue name

    Example:
        @order_event('completed')
        def handle_order_completed(event_data):
            process_order_completion(event_data)
    """
    return event_handler(f"order.{action}", queue_name)


def system_event(action: str, queue_name: Optional[str] = None):
    """Decorator for system-related events.

    Args:
        action: The system action (e.g., 'startup', 'shutdown', 'error')
        queue_name: Optional queue name

    Example:
        @system_event('startup')
        def handle_system_startup(event_data):
            initialize_background_tasks()
    """
    return event_handler(f"system.{action}", queue_name)
