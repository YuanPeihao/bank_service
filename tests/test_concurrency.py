"""Tests for concurrency and thread-safety"""
import pytest
import threading
import time
from src.services.database import Database
from src.services.account_service import AccountService
from src.models.account import AccountCreate, DepositRequest, WithdrawRequest, TransferRequest
from src.utils.exceptions import InsufficientBalanceError


class TestConcurrency:
    """Test concurrent operations for thread-safety"""
    
    def test_concurrent_deposits(self, test_db):
        """Test multiple simultaneous deposits to same account"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        def deposit(amount):
            deposit_data = DepositRequest(amount=amount)
            service.deposit(account.id, deposit_data)
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=deposit, args=(100.0,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        final_account = service.get_account(account.id)
        # Initial: 1000, 10 deposits of 100 each = 2000
        assert final_account.balance == 2000.0
    
    def test_concurrent_withdrawals(self, test_db):
        """Test multiple simultaneous withdrawals from same account"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        
        def withdraw(amount):
            try:
                withdraw_data = WithdrawRequest(amount=amount)
                service.withdraw(account.id, withdraw_data)
            except InsufficientBalanceError:
                pass  # Expected for some threads
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=withdraw, args=(100.0,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        final_account = service.get_account(account.id)
        # Initial: 1000, 5 withdrawals of 100 each = 500
        assert final_account.balance == 500.0
    
    def test_concurrent_transfers(self, test_db):
        """Test multiple simultaneous transfers between accounts"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account1 = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        account2 = service.create_account(AccountCreate(account_number="ACC002", initial_balance=500.0))
        
        def transfer(amount):
            try:
                transfer_data = TransferRequest(to_account_id=account2.id, amount=amount)
                service.transfer(account1.id, transfer_data)
            except InsufficientBalanceError:
                pass
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=transfer, args=(100.0,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        final_account1 = service.get_account(account1.id)
        final_account2 = service.get_account(account2.id)
        
        # Account1: 1000 - (5 * 100) = 500
        # Account2: 500 + (5 * 100) = 1000
        assert final_account1.balance == 500.0
        assert final_account2.balance == 1000.0
    
    def test_concurrent_mixed_operations(self, test_db):
        """Test concurrent deposits, withdrawals, and transfers"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account1 = service.create_account(AccountCreate(account_number="ACC001", initial_balance=1000.0))
        account2 = service.create_account(AccountCreate(account_number="ACC002", initial_balance=500.0))
        
        def deposit():
            deposit_data = DepositRequest(amount=50.0)
            service.deposit(account1.id, deposit_data)
        
        def withdraw():
            try:
                withdraw_data = WithdrawRequest(amount=50.0)
                service.withdraw(account1.id, withdraw_data)
            except InsufficientBalanceError:
                pass
        
        def transfer():
            try:
                transfer_data = TransferRequest(to_account_id=account2.id, amount=50.0)
                service.transfer(account1.id, transfer_data)
            except InsufficientBalanceError:
                pass
        
        threads = []
        # 5 deposits, 5 withdrawals, 5 transfers
        for i in range(5):
            threads.append(threading.Thread(target=deposit))
            threads.append(threading.Thread(target=withdraw))
            threads.append(threading.Thread(target=transfer))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        final_account1 = service.get_account(account1.id)
        final_account2 = service.get_account(account2.id)
        
        # Verify balances are consistent
        # Account1: 1000 + (5*50 deposits) - (5*50 withdrawals) - (5*50 transfers) = 1000
        # Account2: 500 + (5*50 transfers) = 750
        # Note: Some operations may fail due to insufficient balance, so we check ranges
        assert final_account1.balance >= 0
        assert final_account2.balance >= 500
        # Total should be preserved
        total = final_account1.balance + final_account2.balance
        assert total == 1500.0  # Initial total: 1000 + 500
    
    def test_acid_compliance_transfer(self, test_db):
        """Test that transfers are atomic (all-or-nothing)"""
        from src.services import database
        database.db = test_db
        
        service = AccountService()
        account1 = service.create_account(AccountCreate(account_number="ACC001", initial_balance=100.0))
        account2 = service.create_account(AccountCreate(account_number="ACC002", initial_balance=50.0))
        
        # Try to transfer more than available - should fail completely
        transfer_data = TransferRequest(to_account_id=account2.id, amount=200.0)
        
        with pytest.raises(InsufficientBalanceError):
            service.transfer(account1.id, transfer_data)
        
        # Verify neither account was modified
        final_account1 = service.get_account(account1.id)
        final_account2 = service.get_account(account2.id)
        
        assert final_account1.balance == 100.0
        assert final_account2.balance == 50.0

