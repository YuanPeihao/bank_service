"""Tests for account operations"""
import pytest
from fastapi import status
from src.utils.exceptions import NotFoundError, DomainError, InsufficientBalanceError, InvalidAccountError
from src.services.account_service import AccountService
from src.models.account import AccountCreate, DepositRequest, WithdrawRequest
from src.services.database import Database


class TestAccountOperations:
    """Test account CRUD operations"""
    
    def test_create_account_success(self, test_db):
        """Test successful account creation"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account_data = AccountCreate(account_number="ACC001", initial_balance=1000.0)
        account = service.create_account(account_data)
        
        assert account.id == 1
        assert account.account_number == "ACC001"
        assert account.balance == 1000.0
        assert account.id in test_db._accounts
    
    def test_create_account_duplicate_number(self, test_db):
        """Test creating account with duplicate account number fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account_data = AccountCreate(account_number="ACC001", initial_balance=1000.0)
        service.create_account(account_data)
        
        # Try to create another account with same number
        with pytest.raises(DomainError):
            service.create_account(account_data)
    
    def test_create_account_negative_balance(self, test_db):
        """Test creating account with negative balance fails validation"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        # Pydantic should reject this
        with pytest.raises(Exception):  # Pydantic validation error
            account_data = AccountCreate(account_number="ACC001", initial_balance=-100.0)
            service.create_account(account_data)
    
    def test_get_account_success(self, test_db):
        """Test getting existing account"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account_data = AccountCreate(account_number="ACC001", initial_balance=1000.0)
        created = service.create_account(account_data)
        
        retrieved = service.get_account(created.id)
        assert retrieved.id == created.id
        assert retrieved.account_number == "ACC001"
        assert retrieved.balance == 1000.0
    
    def test_get_account_not_found(self, test_db):
        """Test getting non-existent account raises NotFoundError"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        with pytest.raises(NotFoundError):
            service.get_account(999)
    
    def test_get_all_accounts(self, test_db):
        """Test getting all accounts"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account1 = service.create_account(AccountCreate(account_number="ACC001", initial_balance=100.0))
        account2 = service.create_account(AccountCreate(account_number="ACC002", initial_balance=200.0))
        
        all_accounts = service.get_all_accounts()
        assert len(all_accounts) == 2
        assert account1 in all_accounts
        assert account2 in all_accounts


class TestDepositOperations:
    """Test deposit operations"""
    
    def test_deposit_success(self, test_db):
        """Test successful deposit"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        deposit_data = DepositRequest(amount=500.0)
        updated_account = service.deposit(account.id, deposit_data)
        
        assert updated_account.balance == 1500.0
        assert updated_account.id == account.id
    
    def test_deposit_account_not_found(self, test_db):
        """Test deposit to non-existent account fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        deposit_data = DepositRequest(amount=500.0)
        
        with pytest.raises(NotFoundError):
            service.deposit(999, deposit_data)
    
    def test_deposit_zero_amount(self, test_db):
        """Test deposit with zero amount fails validation"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        # Pydantic should reject zero or negative amounts
        with pytest.raises(Exception):
            deposit_data = DepositRequest(amount=0.0)
            service.deposit(account.id, deposit_data)
    
    def test_deposit_negative_amount(self, test_db):
        """Test deposit with negative amount fails validation"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        with pytest.raises(Exception):
            deposit_data = DepositRequest(amount=-100.0)
            service.deposit(account.id, deposit_data)


class TestWithdrawOperations:
    """Test withdrawal operations"""
    
    def test_withdraw_success(self, test_db):
        """Test successful withdrawal"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        withdraw_data = WithdrawRequest(amount=300.0)
        updated_account = service.withdraw(account.id, withdraw_data)
        
        assert updated_account.balance == 700.0
    
    def test_withdraw_insufficient_balance(self, test_db):
        """Test withdrawal with insufficient balance fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=100.0))
        
        withdraw_data = WithdrawRequest(amount=500.0)
        with pytest.raises(InsufficientBalanceError):
            service.withdraw(account.id, withdraw_data)
    
    def test_withdraw_exact_balance(self, test_db):
        """Test withdrawal of exact balance succeeds"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        withdraw_data = WithdrawRequest(amount=1000.0)
        updated_account = service.withdraw(account.id, withdraw_data)
        
        assert updated_account.balance == 0.0
    
    def test_withdraw_account_not_found(self, test_db):
        """Test withdrawal from non-existent account fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        withdraw_data = WithdrawRequest(amount=100.0)
        
        with pytest.raises(NotFoundError):
            service.withdraw(999, withdraw_data)


class TestTransferOperations:
    """Test transfer operations"""
    
    def test_transfer_success(self, test_db):
        """Test successful transfer"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        from_account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        to_account = service.create_account(AccountCreate(account_number="ACC002", initial_balance=500.0))
        
        from src.models.account import TransferRequest
        transfer_data = TransferRequest(to_account_id=to_account.id, amount=300.0)
        updated_from, updated_to = service.transfer(from_account.id, transfer_data)
        
        assert updated_from.balance == 700.0
        assert updated_to.balance == 800.0
    
    def test_transfer_insufficient_balance(self, test_db):
        """Test transfer with insufficient balance fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        from_account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=100.0))
        to_account = service.create_account(AccountCreate(account_number="ACC002", initial_balance=500.0))
        
        from src.models.account import TransferRequest
        transfer_data = TransferRequest(to_account_id=to_account.id, amount=500.0)
        
        with pytest.raises(InsufficientBalanceError):
            service.transfer(from_account.id, transfer_data)
    
    def test_transfer_same_account(self, test_db):
        """Test transfer to same account fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        from src.models.account import TransferRequest
        transfer_data = TransferRequest(to_account_id=account.id, amount=300.0)
        
        with pytest.raises(InvalidAccountError):
            service.transfer(account.id, transfer_data)
    
    def test_transfer_from_account_not_found(self, test_db):
        """Test transfer from non-existent account fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        to_account = service.create_account(AccountCreate(account_number="ACC002", initial_balance=500.0))
        
        from src.models.account import TransferRequest
        transfer_data = TransferRequest(to_account_id=to_account.id, amount=300.0)
        
        with pytest.raises(NotFoundError):
            service.transfer(999, transfer_data)
    
    def test_transfer_to_account_not_found(self, test_db):
        """Test transfer to non-existent account fails"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        from_account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        from src.models.account import TransferRequest
        transfer_data = TransferRequest(to_account_id=999, amount=300.0)
        
        with pytest.raises(NotFoundError):
            service.transfer(from_account.id, transfer_data)
    
    def test_transfer_large_amount(self, test_db):
        """Test transfer with very large amount"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        from_account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000000.0))
        to_account = service.create_account(AccountCreate(account_number="ACC002", initial_balance=500.0))
        
        from src.models.account import TransferRequest
        transfer_data = TransferRequest(to_account_id=to_account.id, amount=999999.0)
        updated_from, updated_to = service.transfer(from_account.id, transfer_data)
        
        assert updated_from.balance == 1.0
        assert updated_to.balance == 1000499.0

