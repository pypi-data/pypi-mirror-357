# Flask-BunnyStream Extension Best Practices

This document outlines the Flask extension best practices implemented in the BunnyStream Flask extension.

## Flask Extension Best Practices Implemented

### 1. **Proper Initialization Patterns**

The extension supports both immediate and lazy initialization:

```python
# Immediate initialization
app = Flask(__name__)
app.config['BUNNYSTREAM_MODE'] = 'producer'
bunnystream = BunnyStream(app)

# Lazy initialization (application factory pattern)
bunnystream = BunnyStream()

def create_app():
    app = Flask(__name__)
    bunnystream.init_app(app)
    return app
```

### 2. **Configuration Management**

#### Flask Config Integration
The extension automatically extracts configuration from Flask's config:

```python
app.config.update({
    'BUNNYSTREAM_MODE': 'producer',  # Required: 'producer' or 'consumer'
    'BUNNYSTREAM_EXCHANGE': 'my_exchange',
    'BUNNYSTREAM_HOST': 'localhost',
    'BUNNYSTREAM_PORT': 5672,
    'BUNNYSTREAM_VHOST': '/',
    'BUNNYSTREAM_USER': 'guest',
    'BUNNYSTREAM_PASSWORD': 'guest'
})
```

#### Explicit Configuration
You can also provide explicit configuration:

```python
from bunnystream import BunnyStreamConfig

config = BunnyStreamConfig(
    mode='producer',
    exchange_name='my_exchange',
    rabbit_host='localhost'
)
bunnystream = BunnyStream(app, config)
```

### 3. **Error Handling and Validation**

#### Custom Exception Class
```python
from flask_bunnystream import BunnyStreamConfigError

try:
    bunnystream = BunnyStream(app)
except BunnyStreamConfigError as e:
    print(f"Configuration error: {e}")
```

#### Comprehensive Error Scenarios
- Missing required configuration
- Invalid BunnyStream configuration
- Warren initialization failures
- Runtime errors when extension not initialized

### 4. **State Management**

#### Initialization State Tracking
```python
if bunnystream.is_initialized:
    warren = bunnystream.get_warren()
```

#### Safe Access Patterns
```python
try:
    warren = bunnystream.get_warren()
    warren.publish('topic', data)
except RuntimeError as e:
    print(f"Extension not initialized: {e}")
```

### 5. **Application Context Integration**

#### Context-Aware Access
```python
from flask_bunnystream import get_bunnystream

@app.route('/publish')
def publish():
    bs = get_bunnystream()  # Gets extension from current app context
    bs.publish('test.topic', {'message': 'hello'})
    return 'Published!'
```

### 6. **Multiple Application Support**

The extension can be used with multiple Flask applications:

```python
bunnystream = BunnyStream()

app1 = Flask('app1')
app1.config['BUNNYSTREAM_MODE'] = 'producer'
bunnystream.init_app(app1)

app2 = Flask('app2')
app2.config['BUNNYSTREAM_MODE'] = 'consumer'
bunnystream.init_app(app2)
```

### 7. **Resource Management**

#### Teardown Handlers
The extension registers teardown handlers for proper cleanup:

```python
# Automatically registered when extension is initialized
app.teardown_appcontext(bunnystream._teardown)
```

### 8. **Type Safety**

#### Comprehensive Type Hints
```python
from typing import Optional, Any
from flask import Flask
from bunnystream import BunnyStreamConfig

class BunnyStream:
    def __init__(self, app: Optional[Flask] = None, config: Optional[BunnyStreamConfig] = None):
        # Implementation with proper type safety
```

### 9. **Convenience Methods**

#### Direct Publishing
```python
# Direct method delegation
bunnystream.publish('topic', data)  # Delegates to warren.publish()
```

#### Configuration Extraction
```python
# Automatic configuration extraction with validation
config = bunnystream._create_config_from_app(app)
```

### 10. **Comprehensive Documentation**

#### Class and Method Docstrings
```python
class BunnyStream:
    """Flask extension for BunnyStream integration.
    
    This extension allows Flask applications to easily integrate with BunnyStream
    messaging service. It supports both immediate and lazy initialization patterns
    common in Flask applications.
    
    Example usage:
        # Immediate initialization
        app = Flask(__name__)
        app.config['BUNNYSTREAM_MODE'] = 'producer'
        bunnystream = BunnyStream(app)
        
        # Lazy initialization (application factory pattern)
        bunnystream = BunnyStream()
        
        def create_app():
            app = Flask(__name__)
            bunnystream.init_app(app)
            return app
    """
```

## Usage Examples

### Basic Usage
```python
from flask import Flask
from flask_bunnystream import BunnyStream

app = Flask(__name__)
app.config['BUNNYSTREAM_MODE'] = 'producer'
bunnystream = BunnyStream(app)

@app.route('/publish')
def publish():
    bunnystream.publish('user.action', {'user_id': 123, 'action': 'login'})
    return 'Message published!'
```

### Application Factory Pattern
```python
from flask_bunnystream import BunnyStream

bunnystream = BunnyStream()

def create_app(config_name):
    app = Flask(__name__)
    
    if config_name == 'production':
        app.config['BUNNYSTREAM_MODE'] = 'producer'
        app.config['BUNNYSTREAM_HOST'] = 'prod-rabbitmq.example.com'
    else:
        app.config['BUNNYSTREAM_MODE'] = 'producer'
        app.config['BUNNYSTREAM_HOST'] = 'localhost'
    
    bunnystream.init_app(app)
    return app
```

### Error Handling
```python
from flask_bunnystream import BunnyStream, BunnyStreamConfigError

try:
    bunnystream = BunnyStream(app)
except BunnyStreamConfigError as e:
    app.logger.error(f"Failed to initialize BunnyStream: {e}")
    # Handle gracefully or exit
```

## Configuration Reference

| Config Key | Description | Required | Default |
|------------|-------------|----------|---------|
| `BUNNYSTREAM_MODE` | BunnyStream mode ('producer' or 'consumer') | Yes | None |
| `BUNNYSTREAM_EXCHANGE` | RabbitMQ exchange name | No | None |
| `BUNNYSTREAM_HOST` | RabbitMQ host | No | None |
| `BUNNYSTREAM_PORT` | RabbitMQ port | No | None |
| `BUNNYSTREAM_VHOST` | RabbitMQ virtual host | No | None |
| `BUNNYSTREAM_USER` | RabbitMQ username | No | None |
| `BUNNYSTREAM_PASSWORD` | RabbitMQ password | No | None |

## Best Practices Summary

1. ✅ **Lazy Initialization**: Support both immediate and lazy initialization patterns
2. ✅ **Configuration Flexibility**: Extract from Flask config or accept explicit config objects
3. ✅ **Error Handling**: Comprehensive error handling with custom exceptions
4. ✅ **State Management**: Track initialization state and provide safe access patterns
5. ✅ **Context Integration**: Work seamlessly with Flask's application context
6. ✅ **Multiple Apps**: Support multiple Flask applications
7. ✅ **Resource Cleanup**: Proper teardown handlers for resource management
8. ✅ **Type Safety**: Comprehensive type hints throughout
9. ✅ **Convenience**: Direct method delegation and easy access patterns
10. ✅ **Documentation**: Comprehensive docstrings and examples

This implementation follows Flask extension development best practices as outlined in the Flask documentation and common patterns used by popular Flask extensions like Flask-SQLAlchemy, Flask-Login, and Flask-Mail.
