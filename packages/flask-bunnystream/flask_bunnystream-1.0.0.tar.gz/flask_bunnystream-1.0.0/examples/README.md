# Flask-BunnyStream Examples

This directory contains comprehensive examples demonstrating various usage patterns and features of the Flask-BunnyStream extension. Each example is organized in its own directory with detailed documentation and runnable code.

## Examples Overview

### 🚀 [Basic Usage](basic_usage/)
**Fundamental extension usage patterns**
- Direct and lazy initialization methods
- Flask config vs explicit configuration
- Application context usage patterns
- Basic message publishing

**Best for**: Getting started, understanding core concepts

### 🎯 [Event Handlers](event_handlers/)
**Decorator-based event handling system**
- `@event_handler` decorator usage
- Specialized decorators (`@user_event`, `@order_event`, `@system_event`)
- Event handler registration and management
- Error handling and isolation

**Best for**: Understanding the event system, building event-driven applications

### 🏗️ [Full Application](full_app/)
**Complete production-ready example**
- Flask web application with REST API
- SQLAlchemy database integration
- Separate event consumer/worker process
- Docker and Docker Compose setup
- Production deployment patterns

**Best for**: Real-world implementation, production deployment reference

## Quick Start Guide

### Choose Your Starting Point

1. **New to Flask-BunnyStream?** → Start with [Basic Usage](basic_usage/)
2. **Want to handle events?** → Check [Event Handlers](event_handlers/)
3. **Building a real application?** → Explore [Full Application](full_app/)

### Prerequisites

All examples require:
```bash
# Install Flask and BunnyStream
pip install flask bunnystream

# Install flask-bunnystream from source
cd /path/to/flask-bunnystream
pip install -e .

# Start RabbitMQ (using Docker)
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3.12-management
```

### Running Examples

Each example directory contains:
- `README.md` - Detailed documentation and usage instructions
- `example.py` or similar - Runnable Python code
- Additional files as needed (requirements.txt, Docker files, etc.)

```bash
# Navigate to any example directory
cd basic_usage/    # or event_handlers/ or full_app/

# Follow the README instructions for that specific example
cat README.md

# Run the example
python example.py
```

## Example Comparison

| Feature | Basic Usage | Event Handlers | Full Application |
|---------|-------------|----------------|------------------|
| **Complexity** | Simple | Moderate | Advanced |
| **Setup Time** | 5 minutes | 10 minutes | 15-30 minutes |
| **Prerequisites** | Flask + RabbitMQ | Flask + RabbitMQ | Docker Compose |
| **Use Case** | Learning basics | Event processing | Production deployment |
| **Database** | None | None | SQLAlchemy + PostgreSQL |
| **Docker** | No | No | Yes (full stack) |
| **Testing** | Basic | Manual triggers | Automated tests |
| **Documentation** | Focused | Comprehensive | Production-ready |

## Common Patterns Demonstrated

### 1. **Extension Initialization**
```python
# Basic pattern (from basic_usage)
bunnystream = BunnyStream(app)

# With config pattern
config = BunnyStreamConfig(...)
bunnystream = BunnyStream(config=config)
bunnystream.init_app(app)
```

### 2. **Event Publishing**
```python
# Simple publishing (basic_usage)
bunnystream.publish('event.name', data)

# Using application context
bs = get_bunnystream()
bs.publish('event.name', data)
```

### 3. **Event Handling**
```python
# Decorator pattern (event_handlers)
@event_handler('user.created')
def handle_user_created(event_data):
    # Process the event
    pass

# Specialized decorators
@user_event('created')
@order_event('completed')
@system_event('startup')
```

### 4. **Production Integration**
```python
# Database integration (full_app)
class ReceivedEvent(db.Model):
    # Store events in database
    pass

# Consumer pattern
class EventConsumer:
    def _handle_event(self, received_event: BaseReceivedEvent):
        # Process events from RabbitMQ
        pass
```

## Development Workflow

### 1. **Start with Basic Usage**
- Understand extension initialization
- Learn configuration options
- Practice message publishing

### 2. **Add Event Handling**
- Implement event handlers with decorators
- Test event triggering and processing
- Handle errors and edge cases

### 3. **Scale to Full Application**
- Add database persistence
- Implement consumer/worker processes
- Add Docker deployment
- Include monitoring and testing

## Configuration Examples

### Development Configuration
```python
app.config.update({
    'BUNNYSTREAM_HOST': 'localhost',
    'BUNNYSTREAM_USER': 'guest',
    'BUNNYSTREAM_PASSWORD': 'guest',
    'BUNNYSTREAM_EXCHANGE': 'dev_events'
})
```

### Production Configuration
```python
app.config.update({
    'BUNNYSTREAM_URL': os.environ.get('RABBITMQ_URL'),
    'BUNNYSTREAM_EXCHANGE': 'prod_events',
    'BUNNYSTREAM_QUEUE': 'prod_queue'
})
```

### Docker Environment
```yaml
# docker-compose.yml (from full_app)
environment:
  BUNNYSTREAM_URL: amqp://admin:password@rabbitmq:5672/
  BUNNYSTREAM_EXCHANGE: events_exchange
  BUNNYSTREAM_QUEUE: events_queue
```

## Testing Patterns

### Unit Testing
```python
# Test event handlers directly
def test_user_handler():
    result = handle_user_created({'user_id': 123})
    assert result['status'] == 'success'
```

### Integration Testing
```python
# Test full event flow
def test_event_flow():
    # Fire event
    bunnystream.publish('user.created', data)
    
    # Verify handler was called
    # Check database state
    # Verify side effects
```

### Load Testing
```python
# From full_app example
python test_app.py load 100  # Fire 100 events
```

## Troubleshooting

### Common Issues Across Examples

1. **RabbitMQ Connection**: Ensure RabbitMQ is running and accessible
2. **Import Errors**: Verify flask-bunnystream is installed correctly
3. **Configuration**: Check all required config parameters are set
4. **Event Handlers**: Ensure handlers are registered properly

### Debug Commands
```bash
# Check RabbitMQ status
docker ps | grep rabbitmq

# Test RabbitMQ connection
curl http://localhost:15672  # Management UI

# Check Python imports
python -c "import flask_bunnystream; print('OK')"
```

## Contributing

When adding new examples:

1. **Create a new directory** with descriptive name
2. **Include README.md** with detailed documentation
3. **Add runnable code** with clear comments
4. **Update this main README** with example description
5. **Test thoroughly** on clean environment

## Resources

### Documentation
- [Extension Best Practices](../EXTENSION_BEST_PRACTICES.md)
- [Decorators Documentation](../DECORATORS.md)
- [BunnyStream Documentation](https://github.com/YisusChrist/bunnystream)

### External Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Support

If you encounter issues with any example:

1. Check the specific example's README for troubleshooting
2. Verify all prerequisites are installed
3. Check the main project documentation
4. Open an issue with detailed error information
