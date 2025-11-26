from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AccountCreate(BaseModel):
    """Schema for creating a new account"""
    account_number: str = Field(..., description="Unique account number")
    initial_balance: float = Field(0.0, ge=0, description="Initial account balance (must be >= 0)")


class AccountResponse(BaseModel):
    """Schema for account response"""
    id: int
    account_number: str
    balance: float
    created_at: datetime

    model_config = {"from_attributes": True}


class DepositRequest(BaseModel):
    """Schema for deposit request"""
    amount: float = Field(..., gt=0, description="Deposit amount (must be > 0)")


class WithdrawRequest(BaseModel):
    """Schema for withdraw request"""
    amount: float = Field(..., gt=0, description="Withdrawal amount (must be > 0)")


class TransferRequest(BaseModel):
    """Schema for transfer request"""
    to_account_id: int = Field(..., description="Destination account ID")
    amount: float = Field(..., gt=0, description="Transfer amount (must be > 0)")


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    account_id: int
    transaction_type: str  # 'deposit', 'withdraw', 'transfer_in', 'transfer_out'
    amount: float
    balance_after: float
    related_account_id: Optional[int] = None  # For transfers
    created_at: datetime

    model_config = {"from_attributes": True}

