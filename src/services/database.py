"""In-memory database storage with thread-safety for ACID compliance"""
import threading
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Account:
    """Account data model"""
    id: int
    account_number: str
    balance: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Transaction:
    """Transaction data model"""
    id: int
    account_id: int
    transaction_type: str  # 'deposit', 'withdraw', 'transfer_in', 'transfer_out'
    amount: float
    balance_after: float
    related_account_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)


class Database:
    """
    Thread-safe in-memory database for accounts and transactions.
    Uses locks to ensure ACID compliance for concurrent operations.
    """
    
    def __init__(self):
        self._accounts: Dict[int, Account] = {}
        self._transactions: Dict[int, Transaction] = {}
        self._account_by_number: Dict[str, int] = {}  # account_number -> account_id
        self._lock = threading.RLock()  # Reentrant lock for nested operations
        self._account_counter = 1
        self._transaction_counter = 1
    
    def create_account(self, account_number: str, initial_balance: float) -> Account:
        """Create a new account atomically"""
        with self._lock:
            # Check if account number already exists
            if account_number in self._account_by_number:
                raise ValueError(f"Account number {account_number} already exists")
            
            account = Account(
                id=self._account_counter,
                account_number=account_number,
                balance=initial_balance
            )
            self._accounts[account.id] = account
            self._account_by_number[account_number] = account.id
            self._account_counter += 1
            return account
    
    def get_account(self, account_id: int) -> Optional[Account]:
        """Get account by ID"""
        with self._lock:
            return self._accounts.get(account_id)
    
    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """Get account by account number"""
        with self._lock:
            account_id = self._account_by_number.get(account_number)
            if account_id:
                return self._accounts.get(account_id)
            return None
    
    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        with self._lock:
            return list(self._accounts.values())
    
    def update_account_balance(self, account_id: int, new_balance: float) -> Account:
        """Update account balance atomically"""
        with self._lock:
            account = self._accounts.get(account_id)
            if not account:
                raise ValueError(f"Account {account_id} not found")
            account.balance = new_balance
            return account
    
    def create_transaction(
        self,
        account_id: int,
        transaction_type: str,
        amount: float,
        balance_after: float,
        related_account_id: Optional[int] = None
    ) -> Transaction:
        """Create a transaction record"""
        with self._lock:
            transaction = Transaction(
                id=self._transaction_counter,
                account_id=account_id,
                transaction_type=transaction_type,
                amount=amount,
                balance_after=balance_after,
                related_account_id=related_account_id
            )
            self._transactions[transaction.id] = transaction
            self._transaction_counter += 1
            return transaction
    
    def get_account_transactions(self, account_id: int) -> List[Transaction]:
        """Get all transactions for an account"""
        with self._lock:
            return [
                t for t in self._transactions.values()
                if t.account_id == account_id
            ]
    
    def execute_transfer(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: float
    ) -> Tuple[Account, Account]:
        """
        Execute a transfer atomically with ACID compliance.
        Uses a single lock to ensure both accounts are updated together.
        """
        with self._lock:
            from_account = self._accounts.get(from_account_id)
            to_account = self._accounts.get(to_account_id)
            
            if not from_account:
                raise ValueError(f"Source account {from_account_id} not found")
            if not to_account:
                raise ValueError(f"Destination account {to_account_id} not found")
            if from_account_id == to_account_id:
                raise ValueError("Cannot transfer to the same account")
            if from_account.balance < amount:
                raise ValueError("Insufficient balance")
            
            # Atomic update of both accounts
            from_account.balance -= amount
            to_account.balance += amount
            
            # Create transaction records
            self.create_transaction(
                from_account_id,
                'transfer_out',
                amount,
                from_account.balance,
                to_account_id
            )
            self.create_transaction(
                to_account_id,
                'transfer_in',
                amount,
                to_account.balance,
                from_account_id
            )
            
            return from_account, to_account


# Global database instance
db = Database()

