# Flask-BunnyStream Complete Example Application

## Overview

This comprehensive example demonstrates a complete Flask application using the `flask-bunnystream` extension with SQLAlchemy integration, event handling, and Docker deployment. The example includes:

### ✅ Completed Features

#### 1. **Flask Web Application** (`app.py`)
- REST API with event firing endpoints
- SQLAlchemy integration with event storage
- Health checks and API documentation
- Event listing with pagination and filtering
- Event processing status management

#### 2. **Event Consumer/Worker** (`consumer.py`)
- Separate process for consuming BunnyStream events
- Uses `BaseReceivedEvent` for proper event deserialization
- Database storage of received events
- Event-specific processing logic
- Graceful shutdown handling

#### 3. **Event Types**
- `UserCreatedEvent`: Example user registration event
- `OrderPlacedEvent`: Example e-commerce order event
- Extensible design for additional event types

#### 4. **Database Integration**
- `ReceivedEvent` model for storing processed events
- Support for both SQLite (development) and PostgreSQL (production)
- Event metadata tracking (type, data, timestamp, processed status)

#### 5. **Docker & Container Orchestration**
- Multi-service Docker Compose setup
- Production configuration with PostgreSQL
- Development configuration with SQLite
- Health checks and service dependencies
- Volume persistence for data

#### 6. **Management & Testing Tools**
- `manage.sh`: Shell script for common operations
- `test_app.py`: Comprehensive API testing script
- `test_integration.py`: Integration testing
- Load testing capabilities

## File Structure

```
examples/full_app/
├── app.py                      # Main Flask application
├── consumer.py                 # Event consumer/worker
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── docker-compose.yml          # Production setup (PostgreSQL)
├── docker-compose.dev.yml      # Development setup (SQLite)
├── manage.sh                   # Management helper script
├── test_app.py                 # API testing script
├── test_integration.py         # Integration tests
├── .dockerignore              # Docker build optimization
└── README.md                   # Comprehensive documentation
```

## API Endpoints

### Event Management
- `POST /api/events/user` - Fire UserCreatedEvent
- `POST /api/events/order` - Fire OrderPlacedEvent
- `GET /api/events` - List received events (with pagination/filtering)
- `PUT /api/events/{id}/processed` - Mark event as processed

### System
- `GET /` - API information
- `GET /health` - Health check

## Quick Start Commands

```bash
# Start development environment
./manage.sh start

# Start production environment  
./manage.sh start-prod

# View service status
./manage.sh status

# View logs
./manage.sh logs
./manage.sh logs web
./manage.sh logs consumer

# Run tests
./manage.sh test

# Run load test
./manage.sh load 50

# Stop all services
./manage.sh stop

# Clean everything
./manage.sh clean
```

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

## Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string
- `BUNNYSTREAM_URL`: RabbitMQ connection URL
- `BUNNYSTREAM_EXCHANGE`: Exchange name
- `BUNNYSTREAM_QUEUE`: Queue name
- `SECRET_KEY`: Flask secret key

### Database Support
- **Development**: SQLite for simplicity
- **Production**: PostgreSQL for scalability

### Service URLs (when running)
- **Web App**: http://localhost:5000
- **Health Check**: http://localhost:5000/health  
- **RabbitMQ Management**: http://localhost:15672 (admin/password)

## Example Usage

### Fire Events
```bash
# User event
curl -X POST http://localhost:5000/api/events/user \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "username": "john", "email": "john@example.com"}'

# Order event  
curl -X POST http://localhost:5000/api/events/order \
  -H "Content-Type: application/json" \
  -d '{"order_id": 456, "user_id": 123, "total_amount": 99.99}'
```

### List Events
```bash
# All events
curl http://localhost:5000/api/events

# With pagination
curl "http://localhost:5000/api/events?limit=10&offset=0"

# Filter by type
curl "http://localhost:5000/api/events?type=UserCreatedEvent"

# Filter by status
curl "http://localhost:5000/api/events?processed=false"
```

## Key Implementation Details

### 1. **BunnyStream Integration**
- Uses `flask-bunnystream` extension for event publishing
- Consumer uses `BaseReceivedEvent` for proper deserialization
- Proper error handling and connection management

### 2. **Event Processing Flow**
1. Web app receives API request
2. Creates event object (UserCreatedEvent/OrderPlacedEvent)
3. Fires event using BunnyStream
4. Consumer receives event via RabbitMQ
5. Consumer stores event in database
6. Consumer processes event based on type
7. Consumer marks event as processed

### 3. **Database Design**
- `ReceivedEvent` model stores all events with metadata
- JSON serialization for event data
- Timestamp tracking and processing status
- Pagination support for event listing

### 4. **Container Orchestration**
- Multi-service setup with proper health checks
- Service dependencies ensure startup order
- Volume persistence for data
- Separate development and production configurations

### 5. **Error Handling**
- Graceful error handling in both web app and consumer
- Database transaction rollback on errors
- Proper HTTP status codes and error messages
- Signal handling for graceful shutdown

## Testing

### Automated Testing
```bash
# Run integration tests
python test_integration.py

# Run comprehensive API tests
python test_app.py

# Run load tests
python test_app.py load 100
```

### Manual Testing
```bash
# Start services
./manage.sh start

# Fire some events
./manage.sh test

# Check service status
./manage.sh status

# View processed events
curl "http://localhost:5000/api/events?limit=5"
```

## Production Considerations

### Security
- Change default passwords for RabbitMQ and PostgreSQL
- Use environment files for sensitive configuration
- Enable HTTPS with proper certificates
- Use proper firewall rules

### Scaling
- Multiple consumer instances for parallel processing
- Database connection pooling
- Load balancer for web instances
- RabbitMQ clustering for high availability

### Monitoring
- Application health checks
- RabbitMQ monitoring via management UI
- Database performance monitoring
- Log aggregation and analysis

## Extension Points

### Adding New Event Types
1. Define event class inheriting from `BaseEvent`
2. Add API endpoint for firing the event
3. Add processing logic in consumer
4. Update documentation

### Custom Processing Logic
- Add business logic in consumer event handlers
- Integrate with external services
- Add event validation and transformation
- Implement retry mechanisms for failed processing

This example provides a solid foundation for building event-driven Flask applications with BunnyStream, demonstrating best practices for production deployment and maintenance.
