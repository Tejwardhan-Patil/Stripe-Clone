import os
import datetime
from fpdf import FPDF
from decimal import Decimal

# Constants
INVOICE_DIRECTORY = 'generated_invoices/'
TAX_RATE = Decimal('0.15')  # 15% tax
CURRENCY_SYMBOL = "$"

# Helper Classes
class InvoiceLineItem:
    def __init__(self, description, quantity, unit_price):
        self.description = description
        self.quantity = quantity
        self.unit_price = Decimal(unit_price)
        self.total_price = self.quantity * self.unit_price

    def __repr__(self):
        return f"{self.description} | Quantity: {self.quantity} | Unit Price: {CURRENCY_SYMBOL}{self.unit_price} | Total: {CURRENCY_SYMBOL}{self.total_price}"

class Invoice:
    def __init__(self, invoice_id, user, line_items, issue_date=None):
        self.invoice_id = invoice_id
        self.user = user
        self.line_items = line_items
        self.issue_date = issue_date if issue_date else datetime.datetime.now()
        self.tax_rate = TAX_RATE
        self.subtotal = self.calculate_subtotal()
        self.tax = self.calculate_tax()
        self.total = self.calculate_total()

    def calculate_subtotal(self):
        return sum(item.total_price for item in self.line_items)

    def calculate_tax(self):
        return self.subtotal * self.tax_rate

    def calculate_total(self):
        return self.subtotal + self.tax

    def __repr__(self):
        return f"Invoice #{self.invoice_id} for {self.user} | Subtotal: {CURRENCY_SYMBOL}{self.subtotal} | Tax: {CURRENCY_SYMBOL}{self.tax} | Total: {CURRENCY_SYMBOL}{self.total}"

# PDF Generator
class InvoicePDF(FPDF):
    def __init__(self, invoice):
        super().__init__()
        self.invoice = invoice
        self.add_page()

    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'INVOICE', 0, 1, 'C')

    def add_invoice_details(self):
        self.set_font('Arial', '', 10)
        self.cell(100, 10, f"Invoice ID: {self.invoice.invoice_id}")
        self.cell(90, 10, f"Date: {self.invoice.issue_date.strftime('%Y-%m-%d')}", 0, 1)
        self.cell(0, 10, f"Customer: {self.invoice.user}", 0, 1)

    def add_line_items(self):
        self.set_font('Arial', 'B', 10)
        self.cell(100, 10, 'Description')
        self.cell(30, 10, 'Quantity', 0, 0, 'C')
        self.cell(30, 10, 'Unit Price', 0, 0, 'C')
        self.cell(30, 10, 'Total', 0, 1, 'C')
        self.set_font('Arial', '', 10)

        for item in self.invoice.line_items:
            self.cell(100, 10, item.description)
            self.cell(30, 10, str(item.quantity), 0, 0, 'C')
            self.cell(30, 10, f"{CURRENCY_SYMBOL}{item.unit_price}", 0, 0, 'C')
            self.cell(30, 10, f"{CURRENCY_SYMBOL}{item.total_price}", 0, 1, 'C')

    def add_totals(self):
        self.cell(160, 10, 'Subtotal:', 0, 0, 'R')
        self.cell(30, 10, f"{CURRENCY_SYMBOL}{self.invoice.subtotal}", 0, 1, 'R')
        self.cell(160, 10, 'Tax (15%):', 0, 0, 'R')
        self.cell(30, 10, f"{CURRENCY_SYMBOL}{self.invoice.tax}", 0, 1, 'R')
        self.cell(160, 10, 'Total:', 0, 0, 'R')
        self.cell(30, 10, f"{CURRENCY_SYMBOL}{self.invoice.total}", 0, 1, 'R')

    def generate_pdf(self, output_path):
        self.add_invoice_details()
        self.add_line_items()
        self.add_totals()
        self.output(output_path)

# Invoice Generator Service
class InvoiceGenerator:
    def __init__(self, invoice_storage=INVOICE_DIRECTORY):
        self.invoice_storage = invoice_storage
        if not os.path.exists(invoice_storage):
            os.makedirs(invoice_storage)

    def generate_invoice_id(self):
        return f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    def generate_invoice(self, user, line_items):
        invoice_id = self.generate_invoice_id()
        invoice = Invoice(invoice_id, user, line_items)
        self.save_invoice(invoice)
        return invoice

    def save_invoice(self, invoice):
        pdf = InvoicePDF(invoice)
        invoice_path = os.path.join(self.invoice_storage, f"{invoice.invoice_id}.pdf")
        pdf.generate_pdf(invoice_path)
        print(f"Invoice {invoice.invoice_id} generated at {invoice_path}")

# Usage
if __name__ == "__main__":
    # Line Items
    line_items = [
        InvoiceLineItem("Web Development Services", 10, 100),
        InvoiceLineItem("Hosting", 12, 25),
        InvoiceLineItem("Domain Registration", 1, 15)
    ]

    user = "Person"

    # Generate Invoice
    invoice_generator = InvoiceGenerator()
    invoice = invoice_generator.generate_invoice(user, line_items)

    print(invoice)