#!/usr/bin/env python3
"""
Test script for the Flask-BunnyStream example application.
This script tests the API endpoints and event flow.
"""

import time
import requests
from typing import Dict, Any


class BunnyStreamTestClient:
    """Test client for the Flask-BunnyStream example app."""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def test_health(self) -> Dict[str, Any]:
        """Test the health endpoint."""
        print("Testing health endpoint...")
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        result = response.json()
        print(f"✓ Health check passed: {result['status']}")
        return result

    def test_api_info(self) -> Dict[str, Any]:
        """Test the root API info endpoint."""
        print("Testing API info endpoint...")
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        result = response.json()
        print(f"✓ API info retrieved: {result['message']}")
        return result

    def fire_user_event(self, user_id: int, username: str, email: str) -> Dict[str, Any]:
        """Fire a UserCreatedEvent."""
        print(f"Firing UserCreatedEvent for user {username}...")

        data = {"user_id": user_id, "username": username, "email": email}

        response = self.session.post(f"{self.base_url}/api/events/user", json=data)
        response.raise_for_status()
        result = response.json()
        print(f"✓ UserCreatedEvent fired: {result['message']}")
        return result

    def fire_order_event(self, order_id: int, user_id: int, total_amount: float) -> Dict[str, Any]:
        """Fire an OrderPlacedEvent."""
        print(f"Firing OrderPlacedEvent for order {order_id}...")

        data = {"order_id": order_id, "user_id": user_id, "total_amount": total_amount}

        response = self.session.post(f"{self.base_url}/api/events/order", json=data)
        response.raise_for_status()
        result = response.json()
        print(f"✓ OrderPlacedEvent fired: {result['message']}")
        return result

    def list_events(self, **params) -> Dict[str, Any]:
        """List events with optional parameters."""
        print("Listing events...")

        response = self.session.get(f"{self.base_url}/api/events", params=params)
        response.raise_for_status()
        result = response.json()

        event_count = len(result["events"])
        total = result["pagination"]["total"]
        print(f"✓ Retrieved {event_count} events (total: {total})")

        return result

    def mark_event_processed(self, event_id: int) -> Dict[str, Any]:
        """Mark an event as processed."""
        print(f"Marking event {event_id} as processed...")

        response = self.session.put(f"{self.base_url}/api/events/{event_id}/processed")
        response.raise_for_status()
        result = response.json()
        print(f"✓ Event {event_id} marked as processed")
        return result


def run_comprehensive_test():
    """Run a comprehensive test of the application."""

    print("=" * 60)
    print("Flask-BunnyStream Example Application Test")
    print("=" * 60)

    client = BunnyStreamTestClient()

    try:
        # Test basic endpoints
        client.test_health()
        client.test_api_info()

        # Get initial event count
        initial_events = client.list_events()
        initial_count = initial_events["pagination"]["total"]
        print(f"Initial event count: {initial_count}")

        # Fire some test events
        user_event = client.fire_user_event(
            user_id=123, username="test_user", email="test@example.com"
        )

        order_event = client.fire_order_event(order_id=456, user_id=123, total_amount=99.99)

        # Wait a moment for events to be processed
        print("Waiting for events to be processed...")
        time.sleep(3)

        # Check if events were received
        updated_events = client.list_events()
        updated_count = updated_events["pagination"]["total"]

        if updated_count > initial_count:
            print(f"✓ Events received! New count: {updated_count}")

            # Show recent events
            recent_events = client.list_events(limit=5)
            for event in recent_events["events"][:3]:
                print(
                    f"  - Event {event['id']}: {event['event_type']} "
                    f"(processed: {event['processed']})"
                )

            # Mark first unprocessed event as processed
            unprocessed_events = client.list_events(processed="false")
            if unprocessed_events["events"]:
                first_event = unprocessed_events["events"][0]
                client.mark_event_processed(first_event["id"])
        else:
            print("⚠ No new events received (consumer might not be running)")

        # Test filtering
        print("\nTesting event filtering...")
        user_events = client.list_events(type="UserCreatedEvent")
        order_events = client.list_events(type="OrderPlacedEvent")

        print(f"UserCreatedEvent count: {len(user_events['events'])}")
        print(f"OrderPlacedEvent count: {len(order_events['events'])}")

        print("\n✓ All tests completed successfully!")

    except requests.exceptions.ConnectionError:
        print("✗ Connection failed. Make sure the application is running on localhost:5000")
        print("  Start with: docker-compose up -d")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True


def run_load_test(num_events: int = 10):
    """Run a simple load test."""

    print(f"\nRunning load test with {num_events} events...")
    client = BunnyStreamTestClient()

    try:
        for i in range(num_events):
            if i % 2 == 0:
                client.fire_user_event(
                    user_id=1000 + i, username=f"user_{i}", email=f"user_{i}@example.com"
                )
            else:
                client.fire_order_event(
                    order_id=2000 + i, user_id=1000 + i - 1, total_amount=round(10.0 + i * 5.99, 2)
                )

            if (i + 1) % 5 == 0:
                print(f"  Fired {i + 1}/{num_events} events...")

        print(f"✓ Load test completed: {num_events} events fired")

        # Wait and check results
        time.sleep(2)
        events = client.list_events(limit=num_events)
        print(f"✓ Total events in system: {events['pagination']['total']}")

    except Exception as e:
        print(f"✗ Load test failed: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "load":
        num_events = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        run_load_test(num_events)
    else:
        success = run_comprehensive_test()
        if not success:
            sys.exit(1)
