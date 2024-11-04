import logging
from datetime import datetime, timedelta

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FraudDetection")

class RuleBasedFraudDetection:
    def __init__(self, transaction_data):
        self.transaction_data = transaction_data
        self.fraudulent_transactions = []

    def detect_fraud(self):
        logger.info("Starting fraud detection.")
        
        for transaction in self.transaction_data:
            rules_broken = []
            
            if self.rule_large_amount(transaction):
                rules_broken.append('large_amount')
            
            if self.rule_suspicious_country(transaction):
                rules_broken.append('suspicious_country')

            if self.rule_high_frequency(transaction):
                rules_broken.append('high_frequency')
                
            if self.rule_multiple_declines(transaction):
                rules_broken.append('multiple_declines')

            if rules_broken:
                logger.warning(f"Fraudulent transaction detected: {transaction['transaction_id']}")
                transaction['rules_broken'] = rules_broken
                self.fraudulent_transactions.append(transaction)
        
        logger.info(f"Fraud detection completed. {len(self.fraudulent_transactions)} fraudulent transactions found.")
        return self.fraudulent_transactions

    def rule_large_amount(self, transaction):
        """Rule: Transaction amount exceeds $10,000"""
        large_amount_threshold = 10000
        if transaction['amount'] > large_amount_threshold:
            logger.debug(f"Transaction {transaction['transaction_id']} flagged by large amount rule.")
            return True
        return False

    def rule_suspicious_country(self, transaction):
        """Rule: Transaction originates from a high-risk country."""
        high_risk_countries = ['North Korea', 'Iran', 'Syria', 'Cuba']
        if transaction['country'] in high_risk_countries:
            logger.debug(f"Transaction {transaction['transaction_id']} flagged by suspicious country rule.")
            return True
        return False

    def rule_high_frequency(self, transaction):
        """Rule: More than 5 transactions from the same card within the last hour."""
        card_number = transaction['card_number']
        transaction_time = transaction['transaction_time']

        recent_transactions = [
            t for t in self.transaction_data
            if t['card_number'] == card_number and
            t['transaction_time'] >= transaction_time - timedelta(hours=1)
        ]

        if len(recent_transactions) > 5:
            logger.debug(f"Transaction {transaction['transaction_id']} flagged by high frequency rule.")
            return True
        return False

    def rule_multiple_declines(self, transaction):
        """Rule: Multiple declined transactions in the last 24 hours."""
        card_number = transaction['card_number']
        transaction_time = transaction['transaction_time']

        declined_transactions = [
            t for t in self.transaction_data
            if t['card_number'] == card_number and
            t['status'] == 'declined' and
            t['transaction_time'] >= transaction_time - timedelta(hours=24)
        ]

        if len(declined_transactions) > 3:
            logger.debug(f"Transaction {transaction['transaction_id']} flagged by multiple declines rule.")
            return True
        return False

# Transaction Data for Testing
transaction_data = [
    {
        'transaction_id': 'txn_001',
        'amount': 50000,
        'country': 'United States',
        'card_number': '1234-5678-9876-5432',
        'transaction_time': datetime.now(),
        'status': 'approved'
    },
    {
        'transaction_id': 'txn_002',
        'amount': 200,
        'country': 'Iran',
        'card_number': '4321-8765-6543-2109',
        'transaction_time': datetime.now() - timedelta(hours=2),
        'status': 'approved'
    },
    {
        'transaction_id': 'txn_003',
        'amount': 300,
        'country': 'United States',
        'card_number': '1234-5678-9876-5432',
        'transaction_time': datetime.now() - timedelta(minutes=30),
        'status': 'approved'
    },
    {
        'transaction_id': 'txn_004',
        'amount': 700,
        'country': 'United States',
        'card_number': '1234-5678-9876-5432',
        'transaction_time': datetime.now() - timedelta(minutes=10),
        'status': 'approved'
    },
    {
        'transaction_id': 'txn_005',
        'amount': 150,
        'country': 'Syria',
        'card_number': '8765-4321-2109-6543',
        'transaction_time': datetime.now() - timedelta(hours=3),
        'status': 'approved'
    },
    {
        'transaction_id': 'txn_006',
        'amount': 1200,
        'country': 'United States',
        'card_number': '4321-8765-6543-2109',
        'transaction_time': datetime.now() - timedelta(minutes=5),
        'status': 'declined'
    },
    {
        'transaction_id': 'txn_007',
        'amount': 4500,
        'country': 'North Korea',
        'card_number': '6543-2109-8765-4321',
        'transaction_time': datetime.now() - timedelta(minutes=15),
        'status': 'approved'
    }
]

# Initializing fraud detection
fraud_detector = RuleBasedFraudDetection(transaction_data)

# Running fraud detection
fraudulent_transactions = fraud_detector.detect_fraud()

# Output the result
if fraudulent_transactions:
    logger.info(f"Fraudulent Transactions: {fraudulent_transactions}")
else:
    logger.info("No fraudulent transactions detected.")