#!/bin/bash

# Flask-BunnyStream Example Application Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
}

# Functions for different operations
start_production() {
    print_info "Starting production environment (PostgreSQL + RabbitMQ + Web + Consumer)..."
    check_docker_compose
    docker-compose up -d
    print_success "Production environment started"
    print_info "Web app: http://localhost:5000"
    print_info "RabbitMQ Management: http://localhost:15672 (admin/password)"
}

start_development() {
    print_info "Starting development environment (SQLite + RabbitMQ + Web + Consumer)..."
    check_docker_compose
    docker-compose -f docker-compose.dev.yml up -d
    print_success "Development environment started"
    print_info "Web app: http://localhost:5000"
    print_info "RabbitMQ Management: http://localhost:15672 (admin/password)"
}

stop_services() {
    print_info "Stopping all services..."
    check_docker_compose
    docker-compose down
    docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
    print_success "All services stopped"
}

clean_all() {
    print_warning "This will remove all containers, volumes, and data!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up everything..."
        check_docker_compose
        docker-compose down -v --remove-orphans
        docker-compose -f docker-compose.dev.yml down -v --remove-orphans 2>/dev/null || true
        
        # Remove any leftover images
        docker images flask-bunnystream* -q | xargs -r docker rmi
        
        print_success "Cleanup completed"
    else
        print_info "Cleanup cancelled"
    fi
}

show_logs() {
    local service="${1:-}"
    check_docker_compose
    
    if [ -z "$service" ]; then
        print_info "Showing logs for all services..."
        docker-compose logs -f
    else
        print_info "Showing logs for $service..."
        docker-compose logs -f "$service"
    fi
}

show_status() {
    print_info "Service status:"
    check_docker_compose
    docker-compose ps
    echo
    
    # Check if services are responding
    print_info "Health checks:"
    
    # Web app health
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        print_success "Web app is healthy"
    else
        print_warning "Web app is not responding"
    fi
    
    # RabbitMQ health
    if curl -s http://localhost:15672 > /dev/null 2>&1; then
        print_success "RabbitMQ Management UI is accessible"
    else
        print_warning "RabbitMQ Management UI is not responding"
    fi
}

rebuild_services() {
    print_info "Rebuilding and restarting services..."
    check_docker_compose
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    print_success "Services rebuilt and restarted"
}

run_tests() {
    print_info "Running application tests..."
    
    # Check if web app is running
    if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
        print_error "Web app is not running. Start it first with: $0 start"
        exit 1
    fi
    
    # Install requests if not available
    python3 -c "import requests" 2>/dev/null || {
        print_info "Installing requests library..."
        pip3 install requests
    }
    
    # Run the test script
    python3 test_app.py
}

run_load_test() {
    local num_events="${1:-10}"
    print_info "Running load test with $num_events events..."
    
    # Check if web app is running
    if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
        print_error "Web app is not running. Start it first with: $0 start"
        exit 1
    fi
    
    # Install requests if not available
    python3 -c "import requests" 2>/dev/null || {
        print_info "Installing requests library..."
        pip3 install requests
    }
    
    # Run the load test
    python3 test_app.py load "$num_events"
}

show_help() {
    echo "Flask-BunnyStream Example Application Helper"
    echo
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  start         Start development environment (SQLite)"
    echo "  start-prod    Start production environment (PostgreSQL)"
    echo "  stop          Stop all services"
    echo "  restart       Rebuild and restart services"
    echo "  clean         Remove all containers and volumes"
    echo "  status        Show service status and health"
    echo "  logs [svc]    Show logs (optionally for specific service)"
    echo "  test          Run application tests"
    echo "  load [num]    Run load test (default: 10 events)"
    echo "  help          Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                # Start development environment"
    echo "  $0 logs web             # Show web app logs"
    echo "  $0 logs consumer        # Show consumer logs"
    echo "  $0 test                 # Run application tests"
    echo "  $0 load 50              # Run load test with 50 events"
    echo
    echo "URLs (when running):"
    echo "  Web App:         http://localhost:5000"
    echo "  Health Check:    http://localhost:5000/health"
    echo "  RabbitMQ UI:     http://localhost:15672 (admin/password)"
}

# Main command handling
case "${1:-}" in
    "start")
        start_development
        ;;
    "start-prod")
        start_production
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        rebuild_services
        ;;
    "clean")
        clean_all
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "${2:-}"
        ;;
    "test")
        run_tests
        ;;
    "load")
        run_load_test "${2:-10}"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo
        show_help
        exit 1
        ;;
esac
