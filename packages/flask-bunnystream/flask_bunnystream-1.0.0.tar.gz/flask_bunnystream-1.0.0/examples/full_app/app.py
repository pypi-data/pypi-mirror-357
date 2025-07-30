"""
Example Flask application demonstrating the flask-bunnystream extension
with SQLAlchemy integration for event handling.
"""

import os
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from bunnystream.events import BaseEvent

from flask_bunnystream import BunnyStreamExtension


# Initialize Flask extensions
db = SQLAlchemy()
bunnystream_ext = BunnyStreamExtension()


class ReceivedEvent(db.Model):
    """Model to store received events from BunnyStream."""

    __tablename__ = "received_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed: Mapped[bool] = mapped_column(default=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "received_at": self.received_at.isoformat(),
            "processed": self.processed,
        }


# Example event classes
class UserCreatedEvent(BaseEvent):
    """Event fired when a user is created."""

    def __init__(self, user_id: int, username: str, email: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.email = email


class OrderPlacedEvent(BaseEvent):
    """Event fired when an order is placed."""

    def __init__(self, order_id: int, user_id: int, total_amount: float):
        super().__init__()
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount


def create_app(config_name: str = "development") -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///events.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # BunnyStream configuration
    app.config["BUNNYSTREAM_URL"] = os.environ.get(
        "BUNNYSTREAM_URL", "amqp://guest:guest@localhost:5672/"
    )
    app.config["BUNNYSTREAM_EXCHANGE"] = os.environ.get("BUNNYSTREAM_EXCHANGE", "events_exchange")
    app.config["BUNNYSTREAM_QUEUE"] = os.environ.get("BUNNYSTREAM_QUEUE", "events_queue")

    # Initialize extensions
    db.init_app(app)
    bunnystream_ext.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register routes
    register_routes(app)

    return app


def register_routes(app: Flask) -> None:
    """Register application routes."""

    @app.route("/")
    def index():
        """Root endpoint with API information."""
        return jsonify(
            {
                "message": "Flask BunnyStream Example API",
                "endpoints": {
                    "fire_user_event": "/api/events/user",
                    "fire_order_event": "/api/events/order",
                    "list_events": "/api/events",
                    "health": "/health",
                },
            }
        )

    @app.route("/health")
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

    @app.route("/api/events/user", methods=["POST"])
    def fire_user_event():
        """Fire a UserCreatedEvent."""
        data = request.get_json()

        if not data or not all(k in data for k in ["user_id", "username", "email"]):
            return jsonify({"error": "Missing required fields: user_id, username, email"}), 400

        try:
            event = UserCreatedEvent(
                user_id=data["user_id"], username=data["username"], email=data["email"]
            )

            # Fire the event using BunnyStream
            bunnystream_ext.bunnystream.fire(event)

            return (
                jsonify(
                    {
                        "message": "UserCreatedEvent fired successfully",
                        "event_id": event.event_id,
                        "user_id": data["user_id"],
                    }
                ),
                201,
            )

        except Exception as e:
            return jsonify({"error": f"Failed to fire event: {str(e)}"}), 500

    @app.route("/api/events/order", methods=["POST"])
    def fire_order_event():
        """Fire an OrderPlacedEvent."""
        data = request.get_json()

        if not data or not all(k in data for k in ["order_id", "user_id", "total_amount"]):
            return (
                jsonify({"error": "Missing required fields: order_id, user_id, total_amount"}),
                400,
            )

        try:
            event = OrderPlacedEvent(
                order_id=data["order_id"],
                user_id=data["user_id"],
                total_amount=float(data["total_amount"]),
            )

            # Fire the event using BunnyStream
            bunnystream_ext.bunnystream.fire(event)

            return (
                jsonify(
                    {
                        "message": "OrderPlacedEvent fired successfully",
                        "event_id": event.event_id,
                        "order_id": data["order_id"],
                    }
                ),
                201,
            )

        except Exception as e:
            return jsonify({"error": f"Failed to fire event: {str(e)}"}), 500

    @app.route("/api/events", methods=["GET"])
    def list_events():
        """List all received events."""
        try:
            # Get query parameters
            limit = request.args.get("limit", 50, type=int)
            offset = request.args.get("offset", 0, type=int)
            event_type = request.args.get("type")
            processed = request.args.get("processed")

            # Build query
            query = ReceivedEvent.query

            if event_type:
                query = query.filter(ReceivedEvent.event_type == event_type)

            if processed is not None:
                processed_bool = processed.lower() in ("true", "1", "yes")
                query = query.filter(ReceivedEvent.processed == processed_bool)

            # Get total count
            total = query.count()

            # Apply pagination and ordering
            events = (
                query.order_by(ReceivedEvent.received_at.desc()).offset(offset).limit(limit).all()
            )

            return jsonify(
                {
                    "events": [event.to_dict() for event in events],
                    "pagination": {
                        "total": total,
                        "offset": offset,
                        "limit": limit,
                        "has_more": offset + limit < total,
                    },
                }
            )

        except Exception as e:
            return jsonify({"error": f"Failed to retrieve events: {str(e)}"}), 500

    @app.route("/api/events/<int:event_id>/processed", methods=["PUT"])
    def mark_event_processed(event_id: int):
        """Mark an event as processed."""
        try:
            event = ReceivedEvent.query.get_or_404(event_id)
            event.processed = True
            db.session.commit()

            return jsonify({"message": "Event marked as processed", "event": event.to_dict()})

        except Exception as e:
            return jsonify({"error": f"Failed to update event: {str(e)}"}), 500


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
