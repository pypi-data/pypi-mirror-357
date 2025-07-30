# Flask-BunnyStream Full Example Application

This is a comprehensive example Flask application demonstrating the use of the `flask-bunnystream` extension with SQLAlchemy integration, event handling, and Docker deployment.

## Features

- **Flask Web Application**: REST API for firing and listing events
- **Event Consumer/Worker**: Separate process for consuming and processing events
- **SQLAlchemy Integration**: Database models for storing received events
- **Docker Support**: Complete containerization with Docker Compose
- **Event Types**: Examples of `UserCreatedEvent` and `OrderPlacedEvent`
- **Health Checks**: Built-in health monitoring endpoints

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web     │───▶│   RabbitMQ      │───▶│  Event Consumer │
│   Application   │    │   (BunnyStream) │    │    Worker       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         │                                              │
         └──────────────────┐           ┌───────────────┘
                            │           │
                     ┌─────────────────┐
                     │   PostgreSQL    │
                     │   Database      │
                     └─────────────────┘
```

## API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint

### Event Endpoints

- `POST /api/events/user` - Fire a UserCreatedEvent
- `POST /api/events/order` - Fire an OrderPlacedEvent
- `GET /api/events` - List all received events (with pagination and filtering)
- `PUT /api/events/{id}/processed` - Mark an event as processed

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git (to clone the repository)

### Using Docker Compose (Recommended)

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd flask-bunnystream/examples/full_app
   ```

2. **Start all services** (PostgreSQL + RabbitMQ + Web + Consumer):
   ```bash
   docker-compose up -d
   ```

3. **Or start with SQLite** (simpler development setup):
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Check service status**:
   ```bash
   docker-compose ps
   ```

5. **View logs**:
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f web
   docker-compose logs -f consumer
   ```

### Manual Setup (Local Development)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e ../../src  # Install flask-bunnystream
   ```

2. **Start RabbitMQ** (using Docker):
   ```bash
   docker run -d --name rabbitmq \
     -p 5672:5672 -p 15672:15672 \
     -e RABBITMQ_DEFAULT_USER=admin \
     -e RABBITMQ_DEFAULT_PASS=password \
     rabbitmq:3.12-management
   ```

3. **Set environment variables**:
   ```bash
   export DATABASE_URL="sqlite:///events.db"
   export BUNNYSTREAM_URL="amqp://admin:password@localhost:5672/"
   export BUNNYSTREAM_EXCHANGE="events_exchange"
   export BUNNYSTREAM_QUEUE="events_queue"
   ```

4. **Start the Flask application**:
   ```bash
   python app.py
   ```

5. **Start the consumer** (in another terminal):
   ```bash
   python consumer.py
   ```

## Usage Examples

### Fire Events

1. **Create a User Event**:
   ```bash
   curl -X POST http://localhost:5000/api/events/user \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 123,
       "username": "john_doe",
       "email": "john@example.com"
     }'
   ```

2. **Create an Order Event**:
   ```bash
   curl -X POST http://localhost:5000/api/events/order \
     -H "Content-Type: application/json" \
     -d '{
       "order_id": 456,
       "user_id": 123,
       "total_amount": 99.99
     }'
   ```

### List Events

1. **Get all events**:
   ```bash
   curl http://localhost:5000/api/events
   ```

2. **Get events with pagination**:
   ```bash
   curl "http://localhost:5000/api/events?limit=10&offset=0"
   ```

3. **Filter by event type**:
   ```bash
   curl "http://localhost:5000/api/events?type=UserCreatedEvent"
   ```

4. **Filter by processed status**:
   ```bash
   curl "http://localhost:5000/api/events?processed=false"
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///events.db` |
| `BUNNYSTREAM_URL` | RabbitMQ connection URL | `amqp://guest:guest@localhost:5672/` |
| `BUNNYSTREAM_EXCHANGE` | RabbitMQ exchange name | `events_exchange` |
| `BUNNYSTREAM_QUEUE` | RabbitMQ queue name | `events_queue` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |

### Database Configuration

The application supports both SQLite (for development) and PostgreSQL (for production):

- **SQLite**: `sqlite:///events.db`
- **PostgreSQL**: `postgresql://user:password@host:5432/database`

## Monitoring

### RabbitMQ Management UI

When using Docker Compose, RabbitMQ Management UI is available at:
- **URL**: http://localhost:15672
- **Username**: admin
- **Password**: password

### Application Health

Check application health:
```bash
curl http://localhost:5000/health
```

### Consumer Logs

Monitor event processing:
```bash
docker-compose logs -f consumer
```

## Development

### Project Structure

```
full_app/
├── app.py                      # Main Flask application
├── consumer.py                 # Event consumer/worker
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Production Docker Compose
├── docker-compose.dev.yml      # Development Docker Compose
└── README.md                   # This file
```

### Adding New Event Types

1. **Define the event class** in `app.py`:
   ```python
   class ProductUpdatedEvent(BaseEvent):
       def __init__(self, product_id: int, name: str, price: float):
           super().__init__()
           self.product_id = product_id
           self.name = name
           self.price = price
   ```

2. **Add an API endpoint** to fire the event:
   ```python
   @app.route('/api/events/product', methods=['POST'])
   def fire_product_event():
       # Implementation here
   ```

3. **Add event processing** in `consumer.py`:
   ```python
   def _process_product_updated_event(self, event_data, event_record):
       # Implementation here
   ```

### Testing

Test the application using the provided examples or create your own:

```bash
# Test event firing
python -c "
import requests
response = requests.post('http://localhost:5000/api/events/user', json={
    'user_id': 123, 'username': 'test', 'email': 'test@example.com'
})
print(response.json())
"

# Test event listing
python -c "
import requests
response = requests.get('http://localhost:5000/api/events')
print(response.json())
"
```

## Troubleshooting

### Common Issues

1. **RabbitMQ Connection Failed**:
   - Ensure RabbitMQ is running and accessible
   - Check the `BUNNYSTREAM_URL` configuration
   - Verify network connectivity in Docker

2. **Database Connection Failed**:
   - Check the `DATABASE_URL` configuration
   - Ensure PostgreSQL is running (if using PostgreSQL)
   - Verify database permissions

3. **Events Not Being Processed**:
   - Check consumer logs: `docker-compose logs consumer`
   - Verify RabbitMQ queue has messages
   - Ensure consumer is connected to the same queue as the web app

4. **Import Errors**:
   - Ensure `flask-bunnystream` is installed: `pip install -e ../../src`
   - Check Python path configuration

### Debug Mode

Enable debug logging by setting environment variables:
```bash
export FLASK_ENV=development
export PYTHONPATH=/app/src
```

### Clean Restart

To completely reset the environment:
```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build -d
```

## Production Deployment

### Security Considerations

1. **Change default passwords**:
   - RabbitMQ admin password
   - PostgreSQL password
   - Flask secret key

2. **Use environment files**:
   ```bash
   # Create .env file
   echo "DATABASE_URL=postgresql://user:password@postgres:5432/events_db" > .env
   echo "BUNNYSTREAM_URL=amqp://user:password@rabbitmq:5672/" >> .env
   echo "SECRET_KEY=$(openssl rand -base64 32)" >> .env
   ```

3. **Enable HTTPS** and use proper reverse proxy (nginx, traefik, etc.)

4. **Set up monitoring** and alerting for production workloads

### Scaling

The application is designed to be scalable:

- **Multiple consumers**: Run multiple consumer instances for parallel event processing
- **Database scaling**: Use PostgreSQL with connection pooling
- **Load balancing**: Place multiple web instances behind a load balancer

## License

This example is provided under the same license as the flask-bunnystream project.
