"""
Event consumer/worker that listens for events from BunnyStream
and stores them in the database.
"""

import json
import logging
import signal
import sys
from datetime import datetime
from typing import Any, Dict

from flask import Flask
from bunnystream import Warren, BunnyStreamConfig
from bunnystream.events import BaseReceivedEvent

from app import create_app, db, ReceivedEvent


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumer class to handle incoming events."""

    def __init__(self, app: Flask):
        self.app = app
        self.bunnystream = None
        self.running = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()

    def start(self) -> None:
        """Start the event consumer."""
        logger.info("Starting event consumer...")

        with self.app.app_context():
            try:
                # Create BunnyStream config for consumer
                config = BunnyStreamConfig(
                    mode="consumer",
                    exchange_name=self.app.config["BUNNYSTREAM_EXCHANGE"],
                    rabbit_host=self.app.config.get("BUNNYSTREAM_HOST", "localhost"),
                    rabbit_port=self.app.config.get("BUNNYSTREAM_PORT", 5672),
                    rabbit_user=self.app.config.get("BUNNYSTREAM_USER", "admin"),
                    rabbit_pass=self.app.config.get("BUNNYSTREAM_PASSWORD", "password"),
                    rabbit_vhost=self.app.config.get("BUNNYSTREAM_VHOST", "/"),
                )

                # Initialize Warren for consuming events
                self.bunnystream = Warren(config)

                self.running = True
                logger.info("Event consumer started, waiting for events...")

                # Start consuming events
                self.bunnystream.start_consuming(self._handle_event)

            except Exception as e:
                logger.error(f"Failed to start event consumer: {e}")
                raise

    def stop(self) -> None:
        """Stop the event consumer."""
        self.running = False

        if self.bunnystream:
            try:
                self.bunnystream.stop_consuming()
                self.bunnystream.disconnect()
                logger.info("Event consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping event consumer: {e}")

    def _handle_event(self, received_event: BaseReceivedEvent) -> None:
        """Handle incoming events and store them in the database."""

        try:
            with self.app.app_context():
                logger.info(f"Received event: {received_event.event_type}")

                # Convert event data to JSON string
                event_data_json = json.dumps(received_event.event_data, default=str)

                # Create database record
                event_record = ReceivedEvent(
                    event_type=received_event.event_type,
                    event_data=event_data_json,
                    received_at=datetime.utcnow(),
                    processed=False,
                )

                # Save to database
                db.session.add(event_record)
                db.session.commit()

                logger.info(
                    f"Event stored in database: ID={event_record.id}, "
                    f"Type={event_record.event_type}"
                )

                # Process specific event types
                self._process_event_by_type(received_event, event_record)

        except Exception as e:
            logger.error(f"Error handling event: {e}")
            # Rollback transaction on error
            with self.app.app_context():
                db.session.rollback()

    def _process_event_by_type(
        self, received_event: BaseReceivedEvent, event_record: ReceivedEvent
    ) -> None:
        """Process events based on their type."""

        try:
            event_type = received_event.event_type
            event_data = received_event.event_data

            if event_type == "UserCreatedEvent":
                self._process_user_created_event(event_data, event_record)
            elif event_type == "OrderPlacedEvent":
                self._process_order_placed_event(event_data, event_record)
            else:
                logger.info(f"No specific processing for event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing event by type: {e}")

    def _process_user_created_event(
        self, event_data: Dict[str, Any], event_record: ReceivedEvent
    ) -> None:
        """Process UserCreatedEvent."""
        user_id = event_data.get("user_id")
        username = event_data.get("username")
        email = event_data.get("email")

        logger.info(
            f"Processing UserCreatedEvent: user_id={user_id}, "
            f"username={username}, email={email}"
        )

        # Here you could add business logic like:
        # - Send welcome email
        # - Create user profile
        # - Update analytics
        # - Trigger other events

        # Mark as processed
        event_record.processed = True
        db.session.commit()

        logger.info("UserCreatedEvent processed successfully")

    def _process_order_placed_event(
        self, event_data: Dict[str, Any], event_record: ReceivedEvent
    ) -> None:
        """Process OrderPlacedEvent."""
        order_id = event_data.get("order_id")
        user_id = event_data.get("user_id")
        total_amount = event_data.get("total_amount")

        logger.info(
            f"Processing OrderPlacedEvent: order_id={order_id}, "
            f"user_id={user_id}, total_amount={total_amount}"
        )

        # Here you could add business logic like:
        # - Send order confirmation email
        # - Update inventory
        # - Process payment
        # - Update user statistics
        # - Trigger fulfillment process

        # Mark as processed
        event_record.processed = True
        db.session.commit()

        logger.info("OrderPlacedEvent processed successfully")


def main():
    """Main entry point for the event consumer."""
    logger.info("Initializing event consumer...")

    try:
        # Create Flask app
        app = create_app()

        # Create and start consumer
        consumer = EventConsumer(app)
        consumer.start()

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")
    except Exception as e:
        logger.error(f"Consumer failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
