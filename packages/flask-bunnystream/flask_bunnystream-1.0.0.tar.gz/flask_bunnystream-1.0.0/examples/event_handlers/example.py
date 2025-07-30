"""Example usage of Flask-BunnyStream event handler decorators."""

from flask import Flask
from flask_bunnystream import (
    BunnyStream,
    event_handler,
    user_event,
    order_event,
    system_event,
    register_pending_handlers,
)


# Example 1: Basic event handler decorator
@event_handler("notification.send")
def handle_notification(event_data):
    """Handle notification sending events."""
    print(f"Sending notification: {event_data.get('message')} to {event_data.get('recipient')}")
    # Your notification logic here
    return {"status": "notification_sent", "data": event_data}


# Example 2: User event handlers using specialized decorator
@user_event("created")
def handle_user_created(event_data):
    """Handle new user creation."""
    user_id = event_data.get("user_id")
    email = event_data.get("email")

    print(f"New user created: {user_id} ({email})")

    # Send welcome email
    print(f"Sending welcome email to {email}")

    # Set up user preferences
    print(f"Setting up default preferences for user {user_id}")

    return {"status": "user_setup_complete", "user_id": user_id}


@user_event("updated", queue_name="user_profile_updates")
def handle_user_updated(event_data):
    """Handle user profile updates."""
    user_id = event_data.get("user_id")
    updated_fields = event_data.get("updated_fields", [])

    print(f"User {user_id} updated fields: {updated_fields}")

    # Sync with external services if email changed
    if "email" in updated_fields:
        print(f"Syncing email update for user {user_id} with external services")

    return {"status": "user_update_processed", "user_id": user_id}


# Example 3: Order event handlers
@order_event("created")
def handle_order_created(event_data):
    """Handle new order creation."""
    order_id = event_data.get("order_id")
    user_id = event_data.get("user_id")
    total = event_data.get("total")

    print(f"New order created: {order_id} for user {user_id}, total: ${total}")

    # Reserve inventory
    print(f"Reserving inventory for order {order_id}")

    # Send order confirmation
    print(f"Sending order confirmation for order {order_id}")

    return {"status": "order_processing_started", "order_id": order_id}


@order_event("completed")
def handle_order_completed(event_data):
    """Handle order completion."""
    order_id = event_data.get("order_id")
    user_id = event_data.get("user_id")

    print(f"Order {order_id} completed for user {user_id}")

    # Send completion notification
    print(f"Sending completion notification for order {order_id}")

    # Update user loyalty points
    print(f"Updating loyalty points for user {user_id}")

    # Generate invoice
    print(f"Generating invoice for order {order_id}")

    return {"status": "order_completion_processed", "order_id": order_id}


# Example 4: System event handlers
@system_event("startup")
def handle_system_startup(event_data):
    """Handle system startup events."""
    print("System startup detected")
    print("Initializing background tasks...")
    print("Checking system health...")

    return {"status": "startup_tasks_complete"}


@system_event("error", queue_name="system_error_queue")
def handle_system_error(event_data):
    """Handle system error events."""
    error_type = event_data.get("error_type")
    error_message = event_data.get("message")
    severity = event_data.get("severity", "medium")

    print(f"System error [{severity}]: {error_type} - {error_message}")

    # Send alert to administrators
    if severity == "high":
        print("Sending high-priority alert to administrators")

    # Log to monitoring system
    print("Logging error to monitoring system")

    return {"status": "error_handled", "severity": severity}


# Example 5: Custom event with multiple handlers
@event_handler("payment.processed")
def handle_payment_accounting(event_data):
    """Handle payment for accounting purposes."""
    payment_id = event_data.get("payment_id")
    amount = event_data.get("amount")

    print(f"Recording payment {payment_id} (${amount}) in accounting system")
    return {"status": "payment_recorded", "payment_id": payment_id}


@event_handler("payment.processed", queue_name="payment_fraud_check")
def handle_payment_fraud_check(event_data):
    """Handle payment fraud checking."""
    payment_id = event_data.get("payment_id")
    user_id = event_data.get("user_id")

    print(f"Running fraud check for payment {payment_id} by user {user_id}")
    # Fraud detection logic here

    return {"status": "fraud_check_complete", "payment_id": payment_id}


def create_app():
    """Create Flask application with BunnyStream and event handlers."""
    app = Flask(__name__)

    # Configure BunnyStream
    app.config.update(
        {
            "BUNNYSTREAM_MODE": "producer",  # or 'consumer' depending on your needs
            "BUNNYSTREAM_EXCHANGE": "events_exchange",
            "BUNNYSTREAM_HOST": "localhost",
            "BUNNYSTREAM_PORT": 5672,
            "BUNNYSTREAM_VHOST": "/",
            "BUNNYSTREAM_USER": "guest",
            "BUNNYSTREAM_PASSWORD": "guest",
        }
    )

    # Initialize BunnyStream extension
    BunnyStream(app)

    # Register all pending event handlers
    register_pending_handlers(app)

    # Routes to trigger events (for demonstration)
    @app.route("/trigger/user_created")
    def trigger_user_created():
        """Trigger user created event."""
        from flask_bunnystream.decorators import trigger_event_handlers

        event_data = {"user_id": 123, "email": "newuser@example.com", "name": "John Doe"}

        # Trigger the event handlers
        trigger_event_handlers(app, "user.created", event_data)

        return {"message": "User created event triggered", "data": event_data}

    @app.route("/trigger/order_completed")
    def trigger_order_completed():
        """Trigger order completed event."""
        from flask_bunnystream.decorators import trigger_event_handlers

        event_data = {
            "order_id": "ORD-456",
            "user_id": 123,
            "total": 99.99,
            "items": ["item1", "item2"],
        }

        # Trigger the event handlers
        trigger_event_handlers(app, "order.completed", event_data)

        return {"message": "Order completed event triggered", "data": event_data}

    @app.route("/trigger/payment_processed")
    def trigger_payment_processed():
        """Trigger payment processed event (multiple handlers)."""
        from flask_bunnystream.decorators import trigger_event_handlers

        event_data = {
            "payment_id": "PAY-789",
            "user_id": 123,
            "amount": 99.99,
            "payment_method": "credit_card",
        }

        # Trigger the event handlers (both accounting and fraud check)
        trigger_event_handlers(app, "payment.processed", event_data)

        return {"message": "Payment processed event triggered", "data": event_data}

    @app.route("/handlers")
    def list_handlers():
        """List all registered event handlers."""
        from flask_bunnystream.decorators import get_all_event_handlers

        all_handlers = get_all_event_handlers(app)

        # Format for display
        handlers_info = {}
        for event_name, handlers in all_handlers.items():
            handlers_info[event_name] = [
                {
                    "function": handler.__name__,
                    "queue_name": getattr(handler, "queue_name", "unknown"),
                }
                for handler in handlers
            ]

        return {"message": "Registered event handlers", "handlers": handlers_info}

    return app


if __name__ == "__main__":
    app = create_app()

    print("Starting Flask app with BunnyStream event handlers...")
    print("\nRegistered event handlers:")

    with app.app_context():
        from flask_bunnystream.decorators import get_all_event_handlers

        all_handlers = get_all_event_handlers(app)

        for event_name, handlers in all_handlers.items():
            print(f"  {event_name}:")
            for handler in handlers:
                queue_name = getattr(handler, "queue_name", "unknown")
                print(f"    - {handler.__name__} (queue: {queue_name})")

    print("\nAvailable routes:")
    print("  GET /trigger/user_created - Trigger user created event")
    print("  GET /trigger/order_completed - Trigger order completed event")
    print("  GET /trigger/payment_processed - Trigger payment processed event")
    print("  GET /handlers - List all registered handlers")

    app.run(debug=True, port=5000)
