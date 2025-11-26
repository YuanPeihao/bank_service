## Task 

Build a banking REST API service with Python FastAPI.

## Functional Requirements

- Create account
- Check account 
- List all accounts
- Deposit to an account
- Withdraw from an account
- Transfer money between accounts

## Non-functional Requirements

- Handles concurrency
- ACID compliant

## Architecture 

3-Tier: Routes -> Services -> Database

## Structure 

src/
|- main.py  # App factory, middleware, exception handlers
|- routes/  # http endpoints
|- services/ # business logic 
|- models/  # Pydantic schemas 
|- utils/  # Errors, logging
tests/  # pytest
requirements.txt
README.md
setup.sh
start.sh  

## Tech Stack

- Python
- FastAPI
- Pydantic
- Pytest

## Data Storage 

- Use in-memory Python dictionary to simplify the database layer

## Error Handling

- Custom Exceptions
    - DomainError -> 400
    - NotFoundError -> 404
    - ValidationError -> 422
    - Exception -> 500
- Response 
    - {"error": "message"}

## Testing

- Account operations (success + failures)
- Transfer money (success, insufficent balance, same account, invalid account)
- Edge cases (zero/negative amounts, invalid UUIDs, large amounts)
- Concurrency (simultaneous deposits, withdrawals, transfers)

## Additional

- Logging 
    - request logging
    - operation logging
    - error logging
- setup.sh : setup Python environment and install dependencies 
- start.sh : load the environment and start the service 
- README.md : quick start, endpoints, examples 
- Add short comments to the complex functions and classes
- Focus on the correctness, data integrity, clean code, good tests coverage and do NOT over-engineer 


