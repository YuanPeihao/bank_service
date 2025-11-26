# Banking REST API Service

A banking REST API service built with Python FastAPI that provides account management, deposits, withdrawals, and money transfers with ACID compliance and thread-safety.

## Features

- **Account Management**: Create, retrieve, and list accounts
- **Deposits**: Deposit money to accounts
- **Withdrawals**: Withdraw money from accounts (with balance validation)
- **Transfers**: Transfer money between accounts (atomic operations)
- **Thread-Safe**: Handles concurrent operations safely
- **ACID Compliant**: Ensures data integrity for all operations
- **Comprehensive Error Handling**: Custom exceptions with appropriate HTTP status codes
- **Logging**: Request, operation, and error logging

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Make setup script executable and run it:
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies

### Start the Service

```bash
chmod +x start.sh
./start.sh
```

The service will start at `http://localhost:8000`

### Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn src.main:app --reload
```

## API Documentation

Once the service is running, you can access:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Accounts

#### Create Account
```http
POST /accounts
Content-Type: application/json

{
  "account_number": "ACC001",
  "initial_balance": 1000.0
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "account_number": "ACC001",
  "balance": 1000.0,
  "created_at": "2024-01-01T12:00:00"
}
```

#### Get Account
```http
GET /accounts/{account_id}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "account_number": "ACC001",
  "balance": 1000.0,
  "created_at": "2024-01-01T12:00:00"
}
```

#### List All Accounts
```http
GET /accounts
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "account_number": "ACC001",
    "balance": 1000.0,
    "created_at": "2024-01-01T12:00:00"
  },
  {
    "id": 2,
    "account_number": "ACC002",
    "balance": 500.0,
    "created_at": "2024-01-01T12:05:00"
  }
]
```

### Deposits

#### Deposit Money
```http
POST /accounts/{account_id}/deposit
Content-Type: application/json

{
  "amount": 500.0
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "account_number": "ACC001",
  "balance": 1500.0,
  "created_at": "2024-01-01T12:00:00"
}
```

### Withdrawals

#### Withdraw Money
```http
POST /accounts/{account_id}/withdraw
Content-Type: application/json

{
  "amount": 300.0
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "account_number": "ACC001",
  "balance": 1200.0,
  "created_at": "2024-01-01T12:00:00"
}
```

**Error Response (400 Bad Request) - Insufficient Balance:**
```json
{
  "error": "Insufficient balance. Current: 100.0, Required: 500.0"
}
```

### Transfers

#### Transfer Money
```http
POST /accounts/{account_id}/transfer
Content-Type: application/json

{
  "to_account_id": 2,
  "amount": 200.0
}
```

**Response (200 OK):**
```json
{
  "from_account": {
    "id": 1,
    "account_number": "ACC001",
    "balance": 800.0,
    "created_at": "2024-01-01T12:00:00"
  },
  "to_account": {
    "id": 2,
    "account_number": "ACC002",
    "balance": 700.0,
    "created_at": "2024-01-01T12:05:00"
  }
}
```

**Error Responses:**
- **400 Bad Request** - Insufficient balance, same account, or invalid operation
- **404 Not Found** - Account not found

### Health Check

#### Health Check
```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

## Error Handling

The API uses custom exceptions that map to appropriate HTTP status codes:

- **400 Bad Request** (`DomainError`): Invalid business logic (e.g., insufficient balance, duplicate account)
- **404 Not Found** (`NotFoundError`): Resource not found
- **422 Unprocessable Entity** (`ValidationError`): Request validation failed
- **500 Internal Server Error**: Unexpected server errors

All error responses follow this format:
```json
{
  "error": "Error message description"
}
```

## Examples

### Example: Complete Banking Flow

```bash
# 1. Create two accounts
curl -X POST http://localhost:8000/accounts \
  -H "Content-Type: application/json" \
  -d '{"account_number": "ACC001", "initial_balance": 1000.0}'

curl -X POST http://localhost:8000/accounts \
  -H "Content-Type: application/json" \
  -d '{"account_number": "ACC002", "initial_balance": 500.0}'

# 2. Deposit to account 1
curl -X POST http://localhost:8000/accounts/1/deposit \
  -H "Content-Type: application/json" \
  -d '{"amount": 200.0}'

# 3. Withdraw from account 1
curl -X POST http://localhost:8000/accounts/1/withdraw \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0}'

# 4. Transfer from account 1 to account 2
curl -X POST http://localhost:8000/accounts/1/transfer \
  -H "Content-Type: application/json" \
  -d '{"to_account_id": 2, "amount": 300.0}'

# 5. Check account balances
curl http://localhost:8000/accounts/1
curl http://localhost:8000/accounts/2
```

## Testing

Run the test suite:

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_accounts.py

# Run with coverage
pytest --cov=src tests/
```

### Test Coverage

The test suite includes:

- ✅ Account operations (create, get, list) - success and failure cases
- ✅ Deposit operations - success, invalid account, zero/negative amounts
- ✅ Withdrawal operations - success, insufficient balance, invalid account
- ✅ Transfer operations - success, insufficient balance, same account, invalid accounts
- ✅ Edge cases - zero/negative amounts, large amounts, invalid IDs
- ✅ Concurrency tests - simultaneous deposits, withdrawals, transfers
- ✅ ACID compliance - atomic transfer operations

## Project Structure

```
bank_service/
├── src/
│   ├── main.py              # FastAPI app factory, middleware, exception handlers
│   ├── routes/
│   │   └── accounts.py      # HTTP endpoint handlers
│   ├── services/
│   │   ├── account_service.py  # Business logic layer
│   │   └── database.py         # In-memory database with thread-safety
│   ├── models/
│   │   └── account.py       # Pydantic schemas
│   └── utils/
│       ├── exceptions.py    # Custom exceptions
│       └── logging.py       # Logging configuration
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_accounts.py     # Account operation tests
│   ├── test_api.py          # API endpoint tests
│   └── test_concurrency.py  # Concurrency and thread-safety tests
├── requirements.txt         # Python dependencies
├── setup.sh                 # Setup script
├── start.sh                 # Start script
└── README.md                # This file
```

## Architecture

The service follows a **3-tier architecture**:

1. **Routes Layer** (`src/routes/`): HTTP endpoints, request/response handling
2. **Services Layer** (`src/services/`): Business logic, validation
3. **Database Layer** (`src/services/database.py`): Data storage with thread-safety

## Data Storage

The service uses an **in-memory Python dictionary** for data storage, which:

- Provides fast operations for development and testing
- Implements thread-safety using `threading.RLock()` for concurrent operations
- Ensures ACID compliance through atomic operations with locks
- **Note**: Data is lost when the service restarts (by design for simplicity)

## Concurrency & ACID Compliance

- **Thread-Safe**: All database operations use reentrant locks (`RLock`) to prevent race conditions
- **Atomic Operations**: Transfers are executed atomically - both accounts are updated together or not at all
- **Isolation**: Concurrent operations are properly isolated using locks
- **Consistency**: Balance checks and updates happen within the same locked section

## Logging

The service logs:

- **Request Logging**: All incoming HTTP requests (method, path)
- **Operation Logging**: Business operations (deposits, withdrawals, transfers)
- **Error Logging**: All errors with full stack traces

Logs are output to stdout in the format:
```
YYYY-MM-DD HH:MM:SS - banking_api - LEVEL - Message
```

## Technology Stack

- **Python 3.8+**: Programming language
- **FastAPI**: Web framework
- **Pydantic**: Data validation and serialization
- **Pytest**: Testing framework
- **Uvicorn**: ASGI server

## License

This project is for educational/demonstration purposes.

