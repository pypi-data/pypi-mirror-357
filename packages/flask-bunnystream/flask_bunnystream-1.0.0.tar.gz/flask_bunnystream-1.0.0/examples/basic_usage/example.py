"""Basic usage examples for Flask-BunnyStream extension."""

from flask import Flask
from bunnystream import BunnyStreamConfig
from flask_bunnystream import BunnyStream, get_bunnystream


# Example 1: Direct initialization with Flask config
def create_app_with_config():
    """Create Flask app with BunnyStream configured via Flask config."""
    app = Flask(__name__)

    # Configure BunnyStream via Flask config
    app.config["BUNNYSTREAM_MODE"] = "producer"  # 'producer' or 'consumer'
    app.config["BUNNYSTREAM_EXCHANGE"] = "my_exchange"
    app.config["BUNNYSTREAM_HOST"] = "localhost"
    app.config["BUNNYSTREAM_PORT"] = 5672
    app.config["BUNNYSTREAM_VHOST"] = "/"
    app.config["BUNNYSTREAM_USER"] = "guest"
    app.config["BUNNYSTREAM_PASSWORD"] = "guest"

    # Initialize extension (config will be extracted from Flask config)
    bunnystream = BunnyStream(app)

    @app.route("/publish")
    def publish_message():
        # Use the extension instance
        bunnystream.publish("test.message", {"hello": "world"})
        return "Message published!"

    @app.route("/publish-context")
    def publish_message_with_context():
        # Or get it from application context
        bs = get_bunnystream()
        bs.publish("test.message", {"hello": "world"})
        return "Message published via context!"

    return app


# Example 2: Lazy initialization with explicit config
def create_app_with_explicit_config():
    """Create Flask app with explicit BunnyStreamConfig."""
    app = Flask(__name__)

    # Create explicit config
    config = BunnyStreamConfig(
        mode="producer",  # 'producer' or 'consumer'
        exchange_name="my_exchange",
        rabbit_host="localhost",
        rabbit_port=5672,
        rabbit_vhost="/",
        rabbit_user="guest",
        rabbit_pass="guest",
    )

    # Initialize with explicit config
    bunnystream = BunnyStream()
    bunnystream.init_app(app, config)

    @app.route("/status")
    def status():
        return f"BunnyStream initialized: {bunnystream.is_initialized}"

    return app


# Example 3: Application factory pattern
bunnystream = BunnyStream()  # Create extension instance


def create_app(config_name="production"):
    """Application factory with lazy initialization."""
    app = Flask(__name__)

    # Configure based on environment
    if config_name == "development":
        app.config.update(
            {
                "BUNNYSTREAM_MODE": "producer",
                "BUNNYSTREAM_EXCHANGE": "dev_exchange",
                "BUNNYSTREAM_HOST": "localhost",
            }
        )
    elif config_name == "production":
        app.config.update(
            {
                "BUNNYSTREAM_MODE": "producer",
                "BUNNYSTREAM_EXCHANGE": "prod_exchange",
                "BUNNYSTREAM_HOST": "prod-rabbitmq.example.com",
            }
        )

    # Initialize extensions
    bunnystream.init_app(app)

    @app.route("/health")
    def health():
        return {"status": "ok", "bunnystream": bunnystream.is_initialized}

    return app


if __name__ == "__main__":
    # Run example 1
    app = create_app_with_config()
    print("Starting Flask app with BunnyStream...")
    print("Visit http://localhost:5000/publish to test")
    app.run(debug=True)
