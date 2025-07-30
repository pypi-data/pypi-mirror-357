# Flask-BunnyStream Basic Usage Example

This example demonstrates the basic usage patterns for the Flask-BunnyStream extension, including different initialization methods and configuration options.

## Overview

The basic usage example shows how to:
- Initialize the BunnyStream extension with Flask
- Configure the extension using Flask config or explicit configuration
- Use both direct extension access and application context patterns
- Publish messages to RabbitMQ

## Files

- `example.py` - Complete basic usage examples with different initialization patterns

## Key Features Demonstrated

### 1. **Direct Initialization with Flask Config**
```python
app = Flask(__name__)

# Configure via Flask config
app.config['BUNNYSTREAM_MODE'] = 'producer'
app.config['BUNNYSTREAM_EXCHANGE'] = 'my_exchange'
app.config['BUNNYSTREAM_HOST'] = 'localhost'
# ... other config options

# Initialize extension
bunnystream = BunnyStream(app)
```

### 2. **Lazy Initialization with Explicit Config**
```python
# Create explicit config
config = BunnyStreamConfig(
    mode='producer',
    exchange_name='my_exchange',
    rabbit_host='localhost',
    # ... other config options
)

# Initialize extension with explicit config
bunnystream = BunnyStream(config=config)
bunnystream.init_app(app)
```

### 3. **Application Context Usage**
```python
@app.route('/publish-context')
def publish_message_with_context():
    # Get extension from application context
    bs = get_bunnystream()
    bs.publish('test.message', {'hello': 'world'})
    return 'Message published!'
```

## Configuration Options

The extension supports configuration through Flask config with the following keys:

| Config Key | Description | Default |
|------------|-------------|---------|
| `BUNNYSTREAM_MODE` | Operation mode: 'producer' or 'consumer' | 'producer' |
| `BUNNYSTREAM_EXCHANGE` | RabbitMQ exchange name | Required |
| `BUNNYSTREAM_HOST` | RabbitMQ host | 'localhost' |
| `BUNNYSTREAM_PORT` | RabbitMQ port | 5672 |
| `BUNNYSTREAM_VHOST` | RabbitMQ virtual host | '/' |
| `BUNNYSTREAM_USER` | RabbitMQ username | 'guest' |
| `BUNNYSTREAM_PASSWORD` | RabbitMQ password | 'guest' |

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
# Run the basic usage example
python example.py

# The app will start on http://localhost:5000
```

### Test the Endpoints
```bash
# Test direct extension usage
curl http://localhost:5000/publish

# Test application context usage
curl http://localhost:5000/publish-context

# Test lazy initialization example
curl http://localhost:5001/publish-lazy
```

## Usage Patterns

### 1. **Direct Extension Access**
Best for simple applications where you have direct access to the extension instance:
```python
bunnystream = BunnyStream(app)

@app.route('/publish')
def publish():
    bunnystream.publish('event.name', data)
    return 'Published!'
```

### 2. **Application Context Access**
Best for larger applications or when using blueprints:
```python
from flask_bunnystream import get_bunnystream

@app.route('/publish')
def publish():
    bs = get_bunnystream()
    bs.publish('event.name', data)
    return 'Published!'
```

### 3. **Configuration-First Approach**
Best for applications with complex configuration requirements:
```python
config = BunnyStreamConfig(
    mode='producer',
    exchange_name='events',
    # ... detailed configuration
)

bunnystream = BunnyStream(config=config)
bunnystream.init_app(app)
```

## Error Handling

The extension provides proper error handling for common scenarios:

- **Missing Configuration**: Clear error messages for required config
- **Connection Failures**: Graceful handling of RabbitMQ connection issues
- **Invalid Configuration**: Validation of configuration parameters

## Next Steps

After understanding the basic usage, explore:

1. **[Event Handlers Example](../event_handlers/)** - Learn about the decorator-based event handling system
2. **[Full Application Example](../full_app/)** - See a complete Flask application with SQLAlchemy integration
3. **[Extension Documentation](../../EXTENSION_BEST_PRACTICES.md)** - Detailed extension usage patterns

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure flask-bunnystream is installed
   ```bash
   pip install -e ../../src
   ```

2. **Connection Refused**: Ensure RabbitMQ is running
   ```bash
   # Check if RabbitMQ is running
   docker ps | grep rabbitmq
   ```

3. **Configuration Error**: Verify all required config parameters are set
   ```python
   # Check your configuration
   print(app.config)
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
