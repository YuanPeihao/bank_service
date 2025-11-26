"""Account service - business logic layer"""
from typing import List, Tuple
from src.services.database import Account
from src.models.account import AccountCreate, DepositRequest, WithdrawRequest, TransferRequest
from src.utils.exceptions import (
    NotFoundError,
    InsufficientBalanceError,
    InvalidAccountError,
    DomainError
)
from src.utils.logging import log_operation, log_error


class AccountService:
    """Service for account operations"""
    
    @property
    def _db(self):
        """Get the database instance dynamically"""
        from src.services import database
        return database.db
    
    def create_account(self, account_data: AccountCreate) -> Account:
        """Create a new account"""
        try:
            log_operation("create_account")
            account = self._db.create_account(
                account_number=account_data.account_number,
                initial_balance=account_data.initial_balance
            )
            log_operation("create_account", account_id=account.id)
            return account
        except ValueError as e:
            log_error(e, "create_account")
            raise DomainError(str(e))
    
    def get_account(self, account_id: int) -> Account:
        """Get account by ID"""
        account = self._db.get_account(account_id)
        if not account:
            raise NotFoundError(f"Account {account_id} not found")
        return account
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return self._db.get_all_accounts()
    
    def deposit(self, account_id: int, deposit_data: DepositRequest) -> Account:
        """
        Deposit money to an account.
        Atomic operation with transaction logging.
        """
        try:
            log_operation("deposit", account_id=account_id)
            account = self._db.get_account(account_id)
            if not account:
                raise NotFoundError(f"Account {account_id} not found")
            
            # Update balance atomically
            new_balance = account.balance + deposit_data.amount
            account = self._db.update_account_balance(account_id, new_balance)
            
            # Log transaction
            self._db.create_transaction(
                account_id=account_id,
                transaction_type='deposit',
                amount=deposit_data.amount,
                balance_after=account.balance
            )
            
            log_operation("deposit", account_id=account_id)
            return account
        except NotFoundError:
            raise
        except Exception as e:
            log_error(e, f"deposit account_id={account_id}")
            raise DomainError(f"Failed to process deposit: {str(e)}")
    
    def withdraw(self, account_id: int, withdraw_data: WithdrawRequest) -> Account:
        """
        Withdraw money from an account.
        Checks for sufficient balance before withdrawal.
        """
        try:
            log_operation("withdraw", account_id=account_id)
            account = self._db.get_account(account_id)
            if not account:
                raise NotFoundError(f"Account {account_id} not found")
            
            if account.balance < withdraw_data.amount:
                raise InsufficientBalanceError(
                    f"Insufficient balance. Current: {account.balance}, Required: {withdraw_data.amount}"
                )
            
            # Update balance atomically
            new_balance = account.balance - withdraw_data.amount
            account = self._db.update_account_balance(account_id, new_balance)
            
            # Log transaction
            self._db.create_transaction(
                account_id=account_id,
                transaction_type='withdraw',
                amount=withdraw_data.amount,
                balance_after=account.balance
            )
            
            log_operation("withdraw", account_id=account_id)
            return account
        except (NotFoundError, InsufficientBalanceError):
            raise
        except Exception as e:
            log_error(e, f"withdraw account_id={account_id}")
            raise DomainError(f"Failed to process withdrawal: {str(e)}")
    
    def transfer(
        self,
        from_account_id: int,
        transfer_data: TransferRequest
    ) -> Tuple[Account, Account]:
        """
        Transfer money between accounts.
        Atomic operation ensuring ACID compliance.
        """
        try:
            log_operation("transfer", account_id=from_account_id)
            
            # Validate accounts are different
            if from_account_id == transfer_data.to_account_id:
                raise InvalidAccountError("Cannot transfer to the same account")
            
            # Execute atomic transfer
            from_account, to_account = self._db.execute_transfer(
                from_account_id=from_account_id,
                to_account_id=transfer_data.to_account_id,
                amount=transfer_data.amount
            )
            
            log_operation("transfer", account_id=from_account_id)
            return from_account, to_account
        except ValueError as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                raise NotFoundError(error_msg)
            elif "insufficient" in error_msg.lower():
                raise InsufficientBalanceError(error_msg)
            elif "same account" in error_msg.lower():
                raise InvalidAccountError(error_msg)
            else:
                raise DomainError(error_msg)
        except (NotFoundError, InsufficientBalanceError, InvalidAccountError):
            raise
        except Exception as e:
            log_error(e, f"transfer from={from_account_id} to={transfer_data.to_account_id}")
            raise DomainError(f"Failed to process transfer: {str(e)}")


# Global service instance
account_service = AccountService()

