"""Account route handlers"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from src.models.account import (
    AccountCreate,
    AccountResponse,
    DepositRequest,
    WithdrawRequest,
    TransferRequest,
    TransactionResponse
)
from src.services.account_service import account_service
from src.utils.exceptions import (
    DomainError,
    NotFoundError,
    InsufficientBalanceError,
    InvalidAccountError
)
from src.utils.logging import log_request, log_error

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(account_data: AccountCreate):
    """Create a new account"""
    log_request("POST", "/accounts")
    try:
        account = account_service.create_account(account_data)
        return AccountResponse(
            id=account.id,
            account_number=account.account_number,
            balance=account.balance,
            created_at=account.created_at
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int):
    """Get account by ID"""
    log_request("GET", f"/accounts/{account_id}")
    try:
        account = account_service.get_account(account_id)
        return AccountResponse(
            id=account.id,
            account_number=account.account_number,
            balance=account.balance,
            created_at=account.created_at
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})


@router.get("", response_model=List[AccountResponse])
async def list_accounts():
    """List all accounts"""
    log_request("GET", "/accounts")
    accounts = account_service.get_all_accounts()
    return [
        AccountResponse(
            id=account.id,
            account_number=account.account_number,
            balance=account.balance,
            created_at=account.created_at
        )
        for account in accounts
    ]


@router.post("/{account_id}/deposit", response_model=AccountResponse)
async def deposit(account_id: int, deposit_data: DepositRequest):
    """Deposit money to an account"""
    log_request("POST", f"/accounts/{account_id}/deposit")
    try:
        account = account_service.deposit(account_id, deposit_data)
        return AccountResponse(
            id=account.id,
            account_number=account.account_number,
            balance=account.balance,
            created_at=account.created_at
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.post("/{account_id}/withdraw", response_model=AccountResponse)
async def withdraw(account_id: int, withdraw_data: WithdrawRequest):
    """Withdraw money from an account"""
    log_request("POST", f"/accounts/{account_id}/withdraw")
    try:
        account = account_service.withdraw(account_id, withdraw_data)
        return AccountResponse(
            id=account.id,
            account_number=account.account_number,
            balance=account.balance,
            created_at=account.created_at
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})
    except InsufficientBalanceError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})


@router.post("/{account_id}/transfer", response_model=dict)
async def transfer(account_id: int, transfer_data: TransferRequest):
    """Transfer money from one account to another"""
    log_request("POST", f"/accounts/{account_id}/transfer")
    try:
        from_account, to_account = account_service.transfer(account_id, transfer_data)
        return {
            "from_account": AccountResponse(
                id=from_account.id,
                account_number=from_account.account_number,
                balance=from_account.balance,
                created_at=from_account.created_at
            ),
            "to_account": AccountResponse(
                id=to_account.id,
                account_number=to_account.account_number,
                balance=to_account.balance,
                created_at=to_account.created_at
            )
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})
    except (InsufficientBalanceError, InvalidAccountError) as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except DomainError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

