import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Database setup
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="transactions")

# Database connection
DATABASE_URL = "postgresql://user:password@localhost:5432/reporting_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Utility function for formatting currency
def format_currency(amount, currency_code):
    return f"{amount / 100:.2f} {currency_code.upper()}"

# Reporting functions
def get_transaction_history(user_id, session):
    """Retrieves all transaction history for a given user."""
    transactions = session.query(Transaction).filter(Transaction.user_id == user_id).all()
    return transactions

def display_transaction_history(user_id, session):
    """Display transaction history in a readable format."""
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        print("User not found.")
        return

    transactions = get_transaction_history(user_id, session)
    
    if not transactions:
        print("No transaction history found for this user.")
        return

    print(f"Transaction History for {user.username} ({user.email})")
    print("-" * 60)
    print(f"{'Date':<20} {'Type':<15} {'Amount':<10} {'Currency':<10} {'Status'}")
    print("-" * 60)

    for transaction in transactions:
        date = transaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
        type_ = transaction.transaction_type
        amount = format_currency(transaction.amount, transaction.currency)
        currency = transaction.currency
        status = transaction.status
        print(f"{date:<20} {type_:<15} {amount:<10} {currency:<10} {status}")

    print("-" * 60)

def generate_transaction_report(start_date, end_date, session):
    """Generate a report of transactions within a specific date range."""
    transactions = session.query(Transaction).filter(
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date
    ).all()

    if not transactions:
        print("No transactions found for the specified period.")
        return

    total_amounts = {}
    for transaction in transactions:
        if transaction.currency not in total_amounts:
            total_amounts[transaction.currency] = 0
        total_amounts[transaction.currency] += transaction.amount

    print(f"Transaction Report from {start_date} to {end_date}")
    print("-" * 60)
    for currency, total_amount in total_amounts.items():
        formatted_total = format_currency(total_amount, currency)
        print(f"Total amount in {currency}: {formatted_total}")
    print("-" * 60)

# Filtering based on transaction type
def filter_transactions_by_type(user_id, transaction_type, session):
    """Filter transactions by type (e.g., payment, refund)."""
    transactions = session.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == transaction_type
    ).all()
    
    if not transactions:
        print(f"No {transaction_type} transactions found.")
        return

    print(f"{transaction_type.capitalize()} Transactions for User ID {user_id}")
    print("-" * 60)
    for transaction in transactions:
        date = transaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
        amount = format_currency(transaction.amount, transaction.currency)
        print(f"{date:<20} {amount:<10} {transaction.status}")
    print("-" * 60)

# Transaction summary for user
def transaction_summary(user_id, session):
    """Generate a summary of transaction statistics for a user."""
    total_transactions = session.query(Transaction).filter(
        Transaction.user_id == user_id
    ).count()

    successful_transactions = session.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.status == 'successful'
    ).count()

    failed_transactions = session.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.status == 'failed'
    ).count()

    print(f"Transaction Summary for User ID {user_id}")
    print("-" * 60)
    print(f"Total Transactions: {total_transactions}")
    print(f"Successful Transactions: {successful_transactions}")
    print(f"Failed Transactions: {failed_transactions}")
    print("-" * 60)

# Main execution block
if __name__ == "__main__":
    session = SessionLocal()

    # Display transaction history for a user
    user_id = 1
    display_transaction_history(user_id, session)

    # Generate transaction report for a specific date range
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 12, 31)
    generate_transaction_report(start_date, end_date, session)

    # Filter transactions by type
    filter_transactions_by_type(user_id, "payment", session)

    # Transaction summary for a user
    transaction_summary(user_id, session)

    session.close()