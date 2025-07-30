# Flask-BunnyStream Event Handlers Example

This example demonstrates the decorator-based event handling system provided by the Flask-BunnyStream extension. It shows how to register event handlers using decorators and how to trigger them when events are received.

## Overview

The event handlers example shows how to:
- Use the `@event_handler` decorator to register event handlers
- Use specialized decorators like `@user_event`, `@order_event`, and `@system_event`
- Handle different types of events with appropriate business logic
- Register and manage event handlers in Flask applications
- Trigger event handlers when events are received

## Files

- `example.py` - Complete event handlers example with various decorator patterns

## Key Features Demonstrated

### 1. **Basic Event Handler Decorator**
```python
@event_handler('notification.send')
def handle_notification(event_data):
    """Handle notification sending events."""
    print(f"Sending notification: {event_data.get('message')}")
    return {"status": "notification_sent"}
```

### 2. **Specialized Event Decorators**
```python
# User events
@user_event('created')
def handle_user_created(event_data):
    """Handle new user creation."""
    user_id = event_data.get('user_id')
    print(f"New user created: {user_id}")

# Order events
@order_event('completed')
def handle_order_completed(event_data):
    """Handle completed orders."""
    order_id = event_data.get('order_id')
    print(f"Order completed: {order_id}")

# System events
@system_event('startup')
def handle_system_startup(event_data):
    """Handle system startup."""
    print("System starting up...")
```

### 3. **Custom Queue Names**
```python
@event_handler('high_priority.task', queue_name='priority_queue')
def handle_priority_task(event_data):
    """Handle high priority tasks with custom queue."""
    # This handler will use 'priority_queue' instead of auto-generated name
    pass
```

### 4. **Event Handler Management**
```python
from flask_bunnystream import register_pending_handlers, get_event_handlers

# Register handlers that were decorated before app context
register_pending_handlers(app)

# Get handlers for a specific event
handlers = get_event_handlers(app, 'user.created')

# Trigger handlers manually (useful for testing)
trigger_event_handlers(app, 'user.created', {'user_id': 123})
```

## Event Handler Decorators

### Core Decorator

#### `@event_handler(event_name, queue_name=None)`
- **event_name**: The name of the event to handle (e.g., 'user.created')
- **queue_name**: Optional custom queue name (auto-generated if not provided)

### Specialized Decorators

#### `@user_event(action, queue_name=None)`
Convenience decorator for user-related events:
- **action**: User action ('created', 'updated', 'deleted', etc.)
- Creates event name as `user.{action}`

#### `@order_event(action, queue_name=None)`
Convenience decorator for order-related events:
- **action**: Order action ('created', 'completed', 'cancelled', etc.)
- Creates event name as `order.{action}`

#### `@system_event(action, queue_name=None)`
Convenience decorator for system-related events:
- **action**: System action ('startup', 'shutdown', 'error', etc.)
- Creates event name as `system.{action}`

## Registration Patterns

### 1. **Global Registration (No App Context)**
```python
# Decorators can be used at module level
@event_handler('global.event')
def global_handler(event_data):
    pass

# Later, register with app
register_pending_handlers(app)
```

### 2. **App Context Registration**
```python
def create_app():
    app = Flask(__name__)
    bunnystream = BunnyStream(app)
    
    # Decorators used within app context are auto-registered
    @event_handler('app.event')
    def app_handler(event_data):
        pass
    
    return app
```

### 3. **Blueprint Registration**
```python
from flask import Blueprint

bp = Blueprint('events', __name__)

@bp.record_once
def register_event_handlers(state):
    app = state.app
    
    @event_handler('blueprint.event')
    def blueprint_handler(event_data):
        pass
    
    register_pending_handlers(app)
```

## Running the Example

### Prerequisites
```bash
# Install dependencies
pip install flask bunnystream

# Install flask-bunnystream (from project root)
pip install -e ../../src
```

### Start RabbitMQ
```bash
# Using Docker
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3.12-management
```

### Run the Example
```bash
# Run the event handlers example
python example.py

# The app will start on http://localhost:5000
```

### Test Event Handling
```bash
# Trigger user creation
curl -X POST http://localhost:5000/trigger/user/created \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "email": "test@example.com"}'

# Trigger order completion
curl -X POST http://localhost:5000/trigger/order/completed \
  -H "Content-Type: application/json" \
  -d '{"order_id": 456, "total": 99.99}'

# Trigger system startup
curl -X POST http://localhost:5000/trigger/system/startup \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0.0"}'

# List registered handlers
curl http://localhost:5000/handlers
```

## Event Handler Flow

```
1. Event Received (from RabbitMQ)
       ↓
2. Event Type Identified
       ↓
3. Matching Handlers Found
       ↓
4. Handlers Executed (with error isolation)
       ↓
5. Results Logged
```

## Error Handling

Event handlers are executed with proper error isolation:

```python
@event_handler('error_prone.event')
def risky_handler(event_data):
    # If this fails, other handlers still execute
    risky_operation()

@event_handler('error_prone.event')
def safe_handler(event_data):
    # This will still run even if risky_handler fails
    safe_operation()
```

Error handling features:
- **Isolated Execution**: Handler failures don't affect other handlers
- **Error Logging**: All errors are logged with context
- **Graceful Degradation**: System continues operating despite handler failures

## Management Functions

### Register Pending Handlers
```python
from flask_bunnystream import register_pending_handlers

# Register all handlers decorated before app initialization
register_pending_handlers(app)
```

### Get Event Handlers
```python
from flask_bunnystream import get_event_handlers, get_all_event_handlers

# Get handlers for specific event
handlers = get_event_handlers(app, 'user.created')

# Get all registered handlers
all_handlers = get_all_event_handlers(app)
```

### Trigger Handlers Manually
```python
from flask_bunnystream import trigger_event_handlers

# Useful for testing or manual event processing
trigger_event_handlers(app, 'user.created', {'user_id': 123})
```

## Best Practices

### 1. **Event Naming Conventions**
- Use dot notation: `domain.action` (e.g., `user.created`, `order.completed`)
- Be specific and descriptive
- Use consistent naming across your application

### 2. **Handler Function Design**
- Keep handlers focused and single-purpose
- Return meaningful status information
- Handle errors gracefully
- Avoid blocking operations

### 3. **Queue Management**
- Use custom queue names for high-priority or specialized handlers
- Consider queue durability and persistence requirements
- Monitor queue lengths and processing times

### 4. **Testing Event Handlers**
```python
def test_user_created_handler():
    with app.app_context():
        # Test handler directly
        result = handle_user_created({'user_id': 123})
        assert result['status'] == 'user_setup_complete'
        
        # Test through trigger mechanism
        trigger_event_handlers(app, 'user.created', {'user_id': 123})
```

## Integration with BunnyStream

The event handlers work seamlessly with the BunnyStream message system:

```python
# Producer side (fires events)
@app.route('/create-user')
def create_user():
    # Create user in database
    user = create_user_in_db()
    
    # Fire event
    bunnystream.fire(UserCreatedEvent(user.id, user.email))
    
    return 'User created!'

# Consumer side (processes events)
@user_event('created')
def handle_user_created(event_data):
    # Process the user creation event
    send_welcome_email(event_data['email'])
    setup_user_preferences(event_data['user_id'])
```

## Next Steps

After understanding event handlers, explore:

1. **[Basic Usage Example](../basic_usage/)** - Learn the fundamental extension usage
2. **[Full Application Example](../full_app/)** - See event handlers in a complete application
3. **[Decorators Documentation](../../DECORATORS.md)** - Detailed decorator system documentation

## Troubleshooting

### Common Issues

1. **Handlers Not Registered**: Call `register_pending_handlers(app)` after app initialization
2. **Event Not Triggering**: Check event name spelling and handler registration
3. **Handler Errors**: Check application logs for handler execution errors

### Debug Information
```python
# Check registered handlers
from flask_bunnystream import get_all_event_handlers
print(get_all_event_handlers(app))

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```
