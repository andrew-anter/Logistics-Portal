Of course. Here is a comprehensive `README.md` file for your project based on all the features we've built. This file includes the setup instructions, API usage, and design notes required by the task.

You can copy and paste this directly into a `README.md` file in your project's root directory.

-----

````markdown
# B2B Logistics Portal

## Objective

This project is a multi-tenant backend system for a fictional logistics SaaS platform. It allows different companies to manage their products, process orders, and perform administrative actions in a secure, isolated environment. The system features asynchronous task processing with Celery and a complete REST API for integration.

---

## Tech Stack

-   **Backend**: Python, Django, Django REST Framework
-   **Database**: PostgreSQL
-   **Asynchronous Tasks**: Celery
-   **Message Broker**: Redis
-   **Containerization**: Docker, Docker Compose
-   **Web Server / Reverse Proxy**: NGINX
-   **Testing**: Pytest

---

## Features

-   **Multi-tenancy**: Securely isolates company data using a subdomain-based approach (e.g., `companya.localhost`).
-   **Role-Based Access Control**: Differentiates between Superusers, company Admins, and Operators.
-   **Product Management**: Basic CRUD operations for company-specific products.
-   **Inventory Control**: A robust, audited stock adjustment service to prevent race conditions and maintain an inventory log.
-   **Asynchronous Order Processing**: Orders are created and then processed in the background by Celery workers, which includes stock deduction.
-   **Asynchronous Data Export**: Admins can export order data to a CSV file, which is generated in the background.
-   **REST API**: A secure, tenant-aware API with token-based authentication.
-   **Custom Django Admin**: The admin interface is customized to respect multi-tenancy rules, with dynamic views and actions based on user permissions.

---

## Setup and Installation

### Prerequisites
-   Docker
-   Docker Compose

### 1. Clone the Repository
```bash
git clone https://github.com/andrew-anter/Logistics-Portal.git
cd Logistics-Portal
````

### 2\. Build and Run the Services

This command will build the Docker image and start all the necessary services (Django, Celery, PostgreSQL, Redis, NGINX).

```bash
docker-compose up --build -d
```

The application will be available at `http://localhost/`.

### 3\. Apply Database Migrations

Run the initial database migrations to set up your tables and create the default user roles.

```bash
docker-compose exec app python manage.py migrate
```

### 4\. Create a Superuser

Create a superuser to access the Django admin. You will be prompted to enter an email and password.

```bash
docker-compose exec app python manage.py createsuperuser
```

You can now log in to the main admin at `http://localhost/admin/`. From here, you can create companies and company-level admin users.

-----

## Usage / API Endpoints

### Authentication

First, obtain an authentication token by making a `POST` request. Use the email and password of a user you created.

```bash
curl -X POST http://<company_domain>.localhost/api/get-token/ \
  -d "email=<user_email>" \
  -d "password=<user_password>"

# Response:
# {"token": "your_auth_token_here"}
```

### API Requests

All subsequent API requests must include the `Authorization` header and the correct `Host` header for the tenant's subdomain.

**List Products (`GET /api/products/`)**

```bash
curl -X GET http://<company_domain>.localhost/api/products/ \
  -H "Authorization: Token your_auth_token_here" \
  -H "Host: <company_domain>.localhost"
```

**Create an Order (`POST /api/orders/`)**

```bash
curl -X POST http://<company_domain>.localhost/api/orders/ \
  -H "Authorization: Token your_auth_token_here" \
  -H "Host: <company_domain>.localhost" \
  -H "Content-Type: application/json" \
  -d '{"product": 1, "quantity": 10}' # Use the primary key of a product
```

**Download an Export (`GET /api/exports/<id>/download/`)**

```bash
curl -X GET http://<company_domain>.localhost/api/exports/1/download/ \
  -H "Authorization: Token your_auth_token_here" \
  -H "Host: <company_domain>.localhost" \
  --output export.csv
```

-----

## Design Notes

### Export Logic

The "Export selected orders" admin action creates an `Export` model instance to track the task and then dispatches a Celery task (`generate_export_file_task`). This task runs in the background, generates the CSV file from the specified orders, and saves it to the `Export` object's `file` field. The status is then updated to `READY`. The user can download the file via the `GET /api/orders/exports/<id>/download/` endpoint.

### Retry Logic

The "Retry failed orders" action (available in the admin) or the `POST /api/orders/<id>/retry/` endpoint is used to re-process an order that has a `FAILED` status. The logic resets the order's `has_been_processed` flag to `False` and its `status` to `PENDING`, and then re-dispatches the `process_order_task` to Celery for another attempt.

-----

## Running Tests

To run the test suite, execute the following command:

```bash
docker-compose exec app pytest
```

```
```
