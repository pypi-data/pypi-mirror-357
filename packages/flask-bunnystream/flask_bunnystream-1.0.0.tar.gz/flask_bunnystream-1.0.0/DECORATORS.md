# Event Handler Decorators

Flask-BunnyStream now provides powerful decorators for registering event handlers that can process messages from RabbitMQ queues.

## Overview

The event handler decorators allow you to easily register functions as handlers for specific events. These handlers will be called when events are received, providing a clean and declarative way to handle messaging patterns.

## Basic Usage

### @event_handler

The main decorator for registering event handlers:

```python
from flask_bunnystream import event_handler

@event_handler('user.created')
def handle_user_created(event_data):
    """Handle user creation events."""
    user_id = event_data.get('user_id')
    email = event_data.get('email')
    
    # Send welcome email
    send_welcome_email(email)
    
    # Set up user preferences
    setup_user_preferences(user_id)
```

With custom queue name:

```python
@event_handler('order.completed', queue_name='order_processing_queue')
def handle_order_completion(event_data):
    """Handle order completion with custom queue."""
    process_order(event_data)
```

## Specialized Decorators

### @user_event

For user-related events:

```python
from flask_bunnystream import user_event

@user_event('created')  # Handles 'user.created'
def handle_user_created(event_data):
    send_welcome_email(event_data['email'])

@user_event('updated')  # Handles 'user.updated'
def handle_user_updated(event_data):
    sync_user_data(event_data)
```

### @order_event

For order-related events:

```python
from flask_bunnystream import order_event

@order_event('created')  # Handles 'order.created'
def handle_new_order(event_data):
    reserve_inventory(event_data)

@order_event('completed')  # Handles 'order.completed'
def handle_order_completion(event_data):
    send_confirmation(event_data)
```

### @system_event

For system-related events:

```python
from flask_bunnystream import system_event

@system_event('startup')  # Handles 'system.startup'
def handle_system_startup(event_data):
    initialize_services()

@system_event('error')  # Handles 'system.error'
def handle_system_error(event_data):
    alert_administrators(event_data)
```

## Multiple Handlers

You can register multiple handlers for the same event:

```python
@event_handler('payment.processed')
def handle_payment_accounting(event_data):
    """Record payment in accounting system."""
    record_payment(event_data)

@event_handler('payment.processed', queue_name='fraud_check_queue')
def handle_payment_fraud_check(event_data):
    """Check payment for fraud."""
    check_for_fraud(event_data)
```

## Flask App Integration

### Basic Setup

```python
from flask import Flask
from flask_bunnystream import BunnyStream, register_pending_handlers

# Define your event handlers
@user_event('created')
def handle_user_created(event_data):
    # Your handler logic
    pass

# Create and configure your Flask app
app = Flask(__name__)
app.config['BUNNYSTREAM_MODE'] = 'consumer'  # or 'producer'
app.config['BUNNYSTREAM_EXCHANGE'] = 'events'

# Initialize BunnyStream
bunnystream = BunnyStream(app)

# Register all pending event handlers
register_pending_handlers(app)
```

### Application Factory Pattern

```python
from flask_bunnystream import BunnyStream, register_pending_handlers

# Create extension instance
bunnystream = BunnyStream()

# Define handlers at module level
@user_event('created')
def handle_user_created(event_data):
    pass

def create_app():
    app = Flask(__name__)
    app.config['BUNNYSTREAM_MODE'] = 'consumer'
    
    # Initialize extension
    bunnystream.init_app(app)
    
    # Register pending handlers
    register_pending_handlers(app)
    
    return app
```

## Handler Management

### List Registered Handlers

```python
from flask_bunnystream.decorators import get_all_event_handlers

@app.route('/handlers')
def list_handlers():
    handlers = get_all_event_handlers(app)
    return {
        event_name: [h.__name__ for h in handler_list]
        for event_name, handler_list in handlers.items()
    }
```

### Get Handlers for Specific Event

```python
from flask_bunnystream.decorators import get_event_handlers

handlers = get_event_handlers(app, 'user.created')
print(f"Found {len(handlers)} handlers for user.created")
```

### Trigger Handlers Manually

```python
from flask_bunnystream.decorators import trigger_event_handlers

# Trigger all handlers for an event
event_data = {'user_id': 123, 'email': 'user@example.com'}
trigger_event_handlers(app, 'user.created', event_data)
```

## Error Handling

Event handlers are automatically wrapped with error handling:

- Errors are logged but don't stop other handlers from running
- Each handler runs in isolation
- The application context is automatically provided

```python
@user_event('created')
def handle_user_created(event_data):
    # If this raises an exception, it will be logged
    # but other handlers will still run
    risky_operation(event_data)
```

## Handler Metadata

Each decorated function gets metadata attributes:

```python
@event_handler('test.event', queue_name='test_queue')
def my_handler(event_data):
    pass

print(my_handler.event_name)        # 'test.event'
print(my_handler.queue_name)        # 'test_queue'
print(my_handler.is_event_handler)  # True
```

## Best Practices

1. **Use descriptive event names**: Follow a pattern like `entity.action` (e.g., `user.created`, `order.completed`)

2. **Keep handlers focused**: Each handler should have a single responsibility

3. **Handle errors gracefully**: Don't let one handler's failure affect others

4. **Use appropriate queue names**: For handlers that need special processing characteristics

5. **Register handlers early**: Call `register_pending_handlers(app)` after BunnyStream initialization

## Example Application

See `examples/event_handlers.py` for a complete working example with:
- Multiple event types
- Multiple handlers per event
- Error handling
- Integration with Flask routes
- Handler listing and triggering

## Testing

Event handlers can be easily tested:

```python
def test_user_created_handler():
    event_data = {'user_id': 123, 'email': 'test@example.com'}
    
    # Call handler directly
    result = handle_user_created(event_data)
    
    # Assert expected behavior
    assert result['status'] == 'user_setup_complete'
```

For integration testing:

```python
def test_event_triggering(app):
    event_data = {'user_id': 123}
    
    with app.app_context():
        trigger_event_handlers(app, 'user.created', event_data)
        # Assert side effects occurred
```
