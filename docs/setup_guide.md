# Setup Guide

## Prerequisites

1. **Node.js**: Install Node.js (>= 14.x).
2. **Python**: Install Python (>= 3.8).
3. **Java**: Install Java (>= 11) for performance-critical services.
4. **Go**: Install Go (>= 1.15) for transaction management and caching.
5. **Docker**: Install Docker for containerized services.
6. **Terraform**: Install Terraform for infrastructure provisioning.
7. **Kubernetes**: Install Kubernetes for managing containerized applications.

## Frontend Setup

1. Navigate to the `frontend/` directory:

    ```bash
    cd frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Start the development server:

    ```bash
    npm start
    ```

## Backend Setup

1. Navigate to the `backend/` directory:

    ```bash
    cd backend
    ```

2. Set up a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Start the backend server:

    ```bash
    python app.py
    ```

## Database Setup

1. Navigate to the `database/` directory:

    ```bash
    cd database
    ```

2. Run migrations:

    ```bash
    python -m migrate
    ```

3. Seed the database:

    ```bash
    python seed_users.py
    ```

## Payment Gateways

1. Configure Stripe and PayPal API keys in `backend/config/env_config.py`:

    ```python
    STRIPE_API_KEY = 'stripe_api_key'
    PAYPAL_API_KEY = 'paypal_api_key'
    ```

## Running Tests

1. Navigate to the `tests/` directory:

    ```bash
    cd tests
    ```

2. Run unit tests:

    ```bash
    pytest
    ```

3. Run end-to-end tests:

    ```bash
    npm run e2e
    ```

## Deployment

1. Build Docker images:

    ```bash
    docker-compose build
    ```

2. Start services using Docker:

    ```bash
    docker-compose up
    ```
