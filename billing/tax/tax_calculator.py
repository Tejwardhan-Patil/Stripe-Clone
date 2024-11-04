from decimal import Decimal
from typing import List, Dict, Optional
from backend.src.models.user_model import User
from backend.src.models.payment_model import Payment
from backend.src.config.env_config import get_tax_rates

class TaxRate:
    def __init__(self, region: str, tax_percent: Decimal):
        self.region = region
        self.tax_percent = tax_percent

    def calculate_tax(self, amount: Decimal) -> Decimal:
        return (self.tax_percent / Decimal(100)) * amount

class TaxCalculator:
    def __init__(self, user: User, items: List[Dict[str, Decimal]]):
        self.user = user
        self.items = items
        self.tax_rates = get_tax_rates()  # Load tax rates from config
        self.applicable_tax_rate = self.get_applicable_tax_rate()

    def get_applicable_tax_rate(self) -> TaxRate:
        """Determines the applicable tax rate based on user's location."""
        region = self.user.address.country
        if region in self.tax_rates:
            return TaxRate(region, self.tax_rates[region])
        else:
            raise ValueError(f"No tax rate available for region: {region}")

    def calculate_item_tax(self, item_amount: Decimal) -> Decimal:
        """Calculates tax for a single item."""
        return self.applicable_tax_rate.calculate_tax(item_amount)

    def calculate_total_tax(self) -> Decimal:
        """Calculates the total tax for the entire transaction."""
        total_tax = Decimal(0)
        for item in self.items:
            total_tax += self.calculate_item_tax(item['amount'])
        return total_tax

    def calculate_grand_total(self) -> Decimal:
        """Calculates the grand total including taxes."""
        total_amount = sum(item['amount'] for item in self.items)
        total_tax = self.calculate_total_tax()
        return total_amount + total_tax

    def generate_tax_breakdown(self) -> Dict[str, Decimal]:
        """Generates a breakdown of taxes per item and the total."""
        tax_breakdown = {}
        total_tax = Decimal(0)
        for item in self.items:
            item_tax = self.calculate_item_tax(item['amount'])
            tax_breakdown[item['description']] = item_tax
            total_tax += item_tax
        return {
            'itemized_taxes': tax_breakdown,
            'total_tax': total_tax,
            'grand_total': self.calculate_grand_total(),
        }

def process_payment_with_tax(user: User, payment: Payment):
    """Processes payment by calculating taxes and updating payment records."""
    tax_calculator = TaxCalculator(user, payment.items)
    tax_breakdown = tax_calculator.generate_tax_breakdown()

    # Update payment object with tax information
    payment.tax_amount = tax_breakdown['total_tax']
    payment.grand_total = tax_breakdown['grand_total']
    payment.tax_breakdown = tax_breakdown['itemized_taxes']

    # Simulate saving payment information (saving to DB)
    payment.save()

    # Return a detailed response for the client
    return {
        'payment_id': payment.id,
        'tax_amount': tax_breakdown['total_tax'],
        'grand_total': tax_breakdown['grand_total'],
        'tax_breakdown': tax_breakdown['itemized_taxes']
    }

# Configuration loading
class ConfigLoader:
    @staticmethod
    def load_tax_config() -> Dict[str, Decimal]:
        """Loads tax configuration."""
        return {
            'US': Decimal('5.00'),
            'EU': Decimal('20.00'),
            'CA': Decimal('13.00')
        }

# Environment Config to load tax rates
def get_tax_rates() -> Dict[str, Decimal]:
    """Loads tax rates from environment configuration or database."""
    return ConfigLoader.load_tax_config()

# Payment Model and User Model (Stubs)
class Payment:
    def __init__(self, items: List[Dict[str, Decimal]], user: User):
        self.items = items
        self.user = user
        self.tax_amount = Decimal(0)
        self.grand_total = Decimal(0)
        self.tax_breakdown = {}

    def save(self):
        """Simulates saving the payment to a database."""
        print(f"Payment {self.id} saved with total {self.grand_total} and tax {self.tax_amount}")

class User:
    def __init__(self, address: Dict[str, str]):
        self.address = address

# Usage
if __name__ == "__main__":
    # User and Payment data
    user = User(address={'country': 'US'})
    items = [
        {'description': 'Item 1', 'amount': Decimal('100.00')},
        {'description': 'Item 2', 'amount': Decimal('200.00')}
    ]

    payment = Payment(items=items, user=user)

    # Process payment and print the results
    result = process_payment_with_tax(user, payment)
    print(result)