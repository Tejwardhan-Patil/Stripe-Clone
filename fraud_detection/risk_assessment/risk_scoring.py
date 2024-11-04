import math
import logging
from datetime import datetime, timedelta

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RiskScoring")

# Risk levels
RISK_LOW = "Low"
RISK_MEDIUM = "Medium"
RISK_HIGH = "High"

# Transaction classes
class Transaction:
    def __init__(self, transaction_id, user_id, amount, timestamp, location, card_type, previous_fraud_score):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.amount = amount
        self.timestamp = timestamp
        self.location = location
        self.card_type = card_type
        self.previous_fraud_score = previous_fraud_score

# User behavior data (historical transaction data)
class UserBehavior:
    def __init__(self, user_id, transaction_history):
        self.user_id = user_id
        self.transaction_history = transaction_history

    def average_transaction_amount(self):
        amounts = [tx.amount for tx in self.transaction_history]
        return sum(amounts) / len(amounts) if amounts else 0

    def frequent_locations(self):
        locations = [tx.location for tx in self.transaction_history]
        return set(locations)

# Risk scoring engine
class RiskScoringEngine:
    def __init__(self, user_behavior_data, rule_weights):
        self.user_behavior_data = user_behavior_data
        self.rule_weights = rule_weights

    def assess_risk(self, transaction):
        logger.info(f"Assessing risk for transaction ID: {transaction.transaction_id}")

        score = 0
        user_behavior = self.user_behavior_data.get(transaction.user_id)

        if user_behavior:
            # Large transaction amounts
            score += self._score_large_amount(transaction, user_behavior)

            # Unusual location
            score += self._score_unusual_location(transaction, user_behavior)

            # Time of transaction
            score += self._score_transaction_time(transaction)

            # Previous fraud score
            score += self._score_previous_fraud(transaction)

            # Card type
            score += self._score_card_type(transaction)

        risk_level = self._determine_risk_level(score)
        logger.info(f"Transaction ID: {transaction.transaction_id}, Risk Score: {score}, Risk Level: {risk_level}")
        return risk_level

    def _score_large_amount(self, transaction, user_behavior):
        average_amount = user_behavior.average_transaction_amount()
        threshold = average_amount * 2
        if transaction.amount > threshold:
            weight = self.rule_weights.get("large_amount", 1)
            return weight * 10  # High penalty for large amounts
        return 0

    def _score_unusual_location(self, transaction, user_behavior):
        frequent_locations = user_behavior.frequent_locations()
        if transaction.location not in frequent_locations:
            weight = self.rule_weights.get("unusual_location", 1)
            return weight * 7  # Medium penalty for unusual location
        return 0

    def _score_transaction_time(self, transaction):
        transaction_hour = transaction.timestamp.hour
        if transaction_hour < 6 or transaction_hour > 22:  # Unusual times
            weight = self.rule_weights.get("transaction_time", 1)
            return weight * 5  # Medium penalty for odd transaction times
        return 0

    def _score_previous_fraud(self, transaction):
        if transaction.previous_fraud_score > 50:
            weight = self.rule_weights.get("previous_fraud_score", 1)
            return weight * 8  # High penalty for prior fraud scores
        return 0

    def _score_card_type(self, transaction):
        if transaction.card_type in ["virtual", "prepaid"]:
            weight = self.rule_weights.get("card_type", 1)
            return weight * 6  # Medium penalty for risky card types
        return 0

    def _determine_risk_level(self, score):
        if score > 25:
            return RISK_HIGH
        elif 10 < score <= 25:
            return RISK_MEDIUM
        else:
            return RISK_LOW

# Helper function for transaction history simulation
def generate_user_behavior(user_id, num_transactions):
    transaction_history = []
    locations = ["New York", "San Francisco", "Los Angeles", "Chicago", "Miami"]
    for i in range(num_transactions):
        tx = Transaction(
            transaction_id=f"TX{i}",
            user_id=user_id,
            amount=round(50 + (i * 10), 2),  # Incrementing amounts
            timestamp=datetime.now() - timedelta(days=i),
            location=locations[i % len(locations)],
            card_type="credit",
            previous_fraud_score=0
        )
        transaction_history.append(tx)
    return UserBehavior(user_id, transaction_history)

# Simulation for assessing risk for a transaction
def simulate_risk_assessment():
    # Simulated rule weights for different rules
    rule_weights = {
        "large_amount": 1.5,
        "unusual_location": 1.2,
        "transaction_time": 1.1,
        "previous_fraud_score": 1.8,
        "card_type": 1.3
    }

    # Simulate user behavior data
    user_behavior_data = {
        "user1": generate_user_behavior("user1", 10),
        "user2": generate_user_behavior("user2", 5)
    }

    # Initialize the Risk Scoring Engine
    engine = RiskScoringEngine(user_behavior_data, rule_weights)

    # Simulate a transaction to assess
    new_transaction = Transaction(
        transaction_id="TX101",
        user_id="user1",
        amount=150.75,
        timestamp=datetime.now(),
        location="Las Vegas",  # Unusual location
        card_type="prepaid",  # Risky card type
        previous_fraud_score=45  # Medium prior fraud score
    )

    # Perform risk assessment
    risk_level = engine.assess_risk(new_transaction)
    logger.info(f"Final Risk Level: {risk_level}")

if __name__ == "__main__":
    simulate_risk_assessment()