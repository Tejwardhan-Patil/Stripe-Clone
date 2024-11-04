# API Documentation

## Authentication

### POST /auth/login

- **Description**: User login using JWT-based authentication.
- **Request**:
  
    ```json
    {
      "email": "person@website.com",
      "password": "password123"
    }
    ```

- **Response**:

    ```json
    {
      "token": "jwt-token"
    }
    ```

### POST /auth/register

- **Description**: Register a new user.
- **Request**:

    ```json
    {
      "email": "person@website.com",
      "password": "password123"
    }
    ```

- **Response**:
  
    ```json
    {
      "message": "Registration successful"
    }
    ```

## Payments

### POST /payments/charge

- **Description**: Charge a payment using Stripe or PayPal.
- **Request**:
  
    ```json
    {
      "amount": 100,
      "currency": "USD",
      "payment_method": "stripe",
      "description": "Product description"
    }
    ```

- **Response**:
  
    ```json
    {
      "status": "success",
      "transaction_id": "txn_1"
    }
    ```

### GET /payments/history

- **Description**: Get payment history for the authenticated user.
- **Response**:
  
    ```json
    [
      {
        "transaction_id": "txn_1",
        "amount": 100,
        "currency": "USD",
        "status": "completed"
      }
    ]
    ```

## Subscriptions

### POST /subscriptions/create

- **Description**: Create a new subscription.
- **Request**:
  
    ```json
    {
      "plan_id": "plan_123",
      "payment_method": "stripe"
    }
    ```

- **Response**:
  
    ```json
    {
      "status": "active",
      "subscription_id": "sub_1"
    }
    ```

### GET /subscriptions

- **Description**: Get all active subscriptions for the authenticated user.
- **Response**:

    ```json
    [
      {
        "subscription_id": "sub_1",
        "status": "active",
        "next_billing_date": "2024-01-01"
      }
    ]
    ```

## Webhooks

### POST /webhooks/stripe

- **Description**: Handles Stripe webhook events.
- **Response**:

    ```json
    {
      "status": "received"
    }
    ```

### POST /webhooks/paypal

- **Description**: Handles PayPal webhook events.
- **Response**:

    ```json
    {
      "status": "received"
    }
    ```

### Error Codes

- **400**: Bad Request
- **401**: Unauthorized
- **404**: Not Found
- **500**: Internal Server Error
