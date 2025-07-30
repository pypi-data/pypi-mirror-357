# Flask-BunnyStream

[![CI](https://github.com/MarcFord/flask-bunnystream/actions/workflows/ci.yml/badge.svg)](https://github.com/MarcFord/flask-bunnystream/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/flask-bunnystream.svg)](https://badge.fury.io/py/flask-bunnystream)
[![Python versions](https://img.shields.io/pypi/pyversions/flask-bunnystream.svg)](https://pypi.org/project/flask-bunnystream/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://codecov.io/gh/MarcFord/flask-bunnystream/branch/main/graph/badge.svg)](https://codecov.io/gh/MarcFord/flask-bunnystream)

A Flask extension for integrating [BunnyStream](https://github.com/MarcFord/bunnystream) messaging system with Flask applications, providing seamless event-driven architecture support.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
  - [Event Handlers](#event-handlers)
- [Examples](#examples)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)
- [Dependencies](#dependencies)
- [Changelog](#changelog)

## Features

- **Flask Extension Pattern**: Follows Flask extension best practices with lazy and immediate initialization
- **Event Handler Decorators**: Decorator-based system for registering event handlers
- **Application Context Integration**: Seamless integration with Flask application context
- **Error Handling**: Robust error handling and graceful degradation
- **Type Safety**: Full type annotations for better development experience
- **Production Ready**: Comprehensive testing and documentation

## Quick Start

### Installation

```bash
# Install from PyPI
pip install flask-bunnystream

# Or install from source
git clone https://github.com/MarcFord/flask-bunnystream.git
cd flask-bunnystream
pip install -e .
```

### Basic Usage

```python
from flask import Flask
from flask_bunnystream import BunnyStream

app = Flask(__name__)

# Configure BunnyStream
app.config['BUNNYSTREAM_MODE'] = 'producer'
app.config['BUNNYSTREAM_EXCHANGE'] = 'my_exchange'
app.config['BUNNYSTREAM_HOST'] = 'localhost'

# Initialize extension
bunnystream = BunnyStream(app)

@app.route('/publish')
def publish_message():
    bunnystream.publish('test.message', {'hello': 'world'})
    return 'Message published!'
```

### Event Handlers

```python
from flask_bunnystream import event_handler, user_event

@event_handler('notification.send')
def handle_notification(event_data):
    print(f"Sending notification: {event_data['message']}")

@user_event('created')
def handle_user_created(event_data):
    print(f"New user: {event_data['user_id']}")
```

## Examples

The `examples/` directory contains comprehensive examples for different use cases:

### 🚀 [Basic Usage](examples/basic_usage/)
Learn the fundamental extension usage patterns:
- Direct and lazy initialization methods
- Flask config vs explicit configuration  
- Application context usage patterns
- Basic message publishing

### 🎯 [Event Handlers](examples/event_handlers/) 
Understand the decorator-based event handling system:
- `@event_handler` decorator usage
- Specialized decorators (`@user_event`, `@order_event`, `@system_event`)
- Event handler registration and management
- Error handling and isolation

### 🏗️ [Full Application](examples/full_app/)
Complete production-ready example:
- Flask web application with REST API
- SQLAlchemy database integration
- Separate event consumer/worker process
- Docker and Docker Compose setup
- Production deployment patterns

## Configuration

The extension supports configuration through Flask config:

| Config Key | Description | Default |
|------------|-------------|---------|
| `BUNNYSTREAM_MODE` | Operation mode: 'producer' or 'consumer' | 'producer' |
| `BUNNYSTREAM_EXCHANGE` | RabbitMQ exchange name | Required |
| `BUNNYSTREAM_HOST` | RabbitMQ host | 'localhost' |
| `BUNNYSTREAM_PORT` | RabbitMQ port | 5672 |
| `BUNNYSTREAM_VHOST` | RabbitMQ virtual host | '/' |
| `BUNNYSTREAM_USER` | RabbitMQ username | 'guest' |
| `BUNNYSTREAM_PASSWORD` | RabbitMQ password | 'guest' |

## API Reference

### Extension Class

#### `BunnyStream(app=None, config=None)`
Main Flask extension class.

**Methods:**
- `init_app(app, config=None)` - Initialize with Flask app
- `publish(*args, **kwargs)` - Publish message to RabbitMQ
- `is_initialized` - Check if extension is initialized
- `warren` - Access underlying BunnyStream Warren instance

### Event Decorators

#### `@event_handler(event_name, queue_name=None)`
Register a function as an event handler.

#### `@user_event(action, queue_name=None)`
Convenience decorator for user events (`user.{action}`).

#### `@order_event(action, queue_name=None)`
Convenience decorator for order events (`order.{action}`).

#### `@system_event(action, queue_name=None)`
Convenience decorator for system events (`system.{action}`).

### Utility Functions

#### `get_bunnystream()`
Get BunnyStream extension from application context.

#### `register_pending_handlers(app)`
Register handlers that were decorated before app initialization.

## Development

### Prerequisites

- Python 3.8+
- RabbitMQ server
- Flask 2.0+
- BunnyStream 1.0.5+

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd flask-bunnystream

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-mock pytest-cov
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=flask_bunnystream

# Run specific test file
python -m pytest tests/test_extension.py -v
```

### Testing with RabbitMQ

```bash
# Start RabbitMQ using Docker
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3.12-management

# RabbitMQ Management UI: http://localhost:15672 (guest/guest)
```

## Architecture

The extension follows Flask extension patterns and integrates with BunnyStream:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │───▶│  BunnyStream    │───▶│   RabbitMQ      │
│                 │    │  Extension      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Event Handlers  │    │     Warren      │    │   Consumers     │
│   (Decorators)  │    │   (BunnyStream) │    │   (Workers)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

### Quick Contributing Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
4. **Make your changes** and add tests
5. **Run the test suite** (`pytest`)
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to your branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/flask-bunnystream.git
cd flask-bunnystream

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Start RabbitMQ for testing
docker run -d --name rabbitmq-dev \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:3.12-management
```

### Code Quality Standards

We maintain high code quality standards:

- **Code Formatting**: Black
- **Security**: Bandit, Safety
- **Testing**: Pytest with coverage

```bash
# Check code quality
black --check src/ tests/ examples/

# Run tests
pytest --cov=flask_bunnystream
```

## Support

### Getting Help

- **📖 Documentation**: Check our comprehensive [examples](examples/) and guides
- **🐛 Bug Reports**: Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml)
- **💡 Feature Requests**: Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml)
- **❓ Questions**: Use our [question template](.github/ISSUE_TEMPLATE/question.yml)
- **💬 Discussions**: Join our [GitHub Discussions](../../discussions)

### Resources

- **[Extension Best Practices](EXTENSION_BEST_PRACTICES.md)** - Detailed extension usage patterns
- **[Decorators Documentation](DECORATORS.md)** - Event handler system documentation
- **[Examples Directory](examples/)** - Comprehensive usage examples
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[BunnyStream Documentation](https://github.com/YisusChrist/bunnystream)** - Underlying messaging system

### Community

- **GitHub Issues**: [Report bugs and request features](../../issues)
- **GitHub Discussions**: [Community discussions and Q&A](../../discussions)
- **Pull Requests**: [Contribute code improvements](../../pulls)

### Supported Versions

| Version | Python Support | Flask Support | Status |
|---------|---------------|---------------|---------|
| 1.x     | 3.8 - 3.12    | 2.0+         | ✅ Active |

## License

This project is licensed under the **GNU General Public License v3.0 or later (GPL-3.0-or-later)** - see the [LICENSE](LICENSE) file for details.

### GPL v3 License Summary

- ✅ **Commercial use** - Use in commercial projects
- ✅ **Modification** - Modify the source code
- ✅ **Distribution** - Distribute the software
- ✅ **Private use** - Use privately
- ✅ **Patent use** - Use patents from contributors
- ⚠️ **Disclose source** - Must provide source code when distributing
- ⚠️ **License and copyright notice** - Must include license and copyright notice
- ⚠️ **Same license** - Derivative works must use the same license
- ⚠️ **State changes** - Must indicate changes made to the code
- ❌ **Liability** - Authors not liable for damages
- ❌ **Warranty** - No warranty provided

### Third-Party Licenses

This project depends on:
- **Flask** (BSD-3-Clause License)
- **BunnyStream** (MIT License)
- **RabbitMQ** (Mozilla Public License 2.0)

## Dependencies

### Core Dependencies

- **[Flask](https://flask.palletsprojects.com/)** - Web framework (≥2.0.0)
- **[BunnyStream](https://github.com/YisusChrist/bunnystream)** - Messaging system (≥1.0.5)

### Runtime Requirements

- **Python** 3.8 - 3.12
- **RabbitMQ** server (any recent version)

### Development Dependencies

See [requirements-dev.txt](requirements-dev.txt) for a complete list of development dependencies.

## Changelog

### v1.0.0 (Current)

#### 🎉 Initial Release
- ✅ Flask extension with lazy and immediate initialization
- ✅ Event handler decorator system (`@event_handler`, `@user_event`, etc.)
- ✅ Comprehensive examples and documentation
- ✅ Production-ready with full test coverage (77 tests)
- ✅ Docker and Docker Compose support
- ✅ Type safety with full type annotations
- ✅ CI/CD with GitHub Actions
- ✅ PyPI publishing automation

#### 🔧 Technical Features
- **Extension Pattern**: Follows Flask extension best practices
- **Error Handling**: Robust error handling and graceful degradation
- **Application Context**: Seamless integration with Flask application context
- **Configuration**: Flexible configuration via Flask config or explicit config
- **Testing**: Comprehensive test suite with integration tests

#### 📦 Package Features
- **Multiple Examples**: Basic usage, event handlers, and full application
- **Documentation**: Detailed guides and API reference
- **Code Quality**: Black, Bandit, and Safety integration
- **CI/CD**: Automated testing and publishing to PyPI

For detailed changes and migration guides, see our [GitHub Releases](../../releases).

---

**Star ⭐ this repository if you find it useful!**

Made with ❤️ by [Marc Ford](https://github.com/MarcFord)
