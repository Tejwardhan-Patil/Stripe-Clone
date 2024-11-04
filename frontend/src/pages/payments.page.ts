import { Component, OnInit } from '@angular/core';
import { PaymentService } from '../api/payment.service';
import { Observable } from 'rxjs';
import { Router } from '@angular/router';
import { map, catchError } from 'rxjs/operators';

@Component({
  selector: 'app-payments',
  templateUrl: './payments.page.html',
  styleUrls: ['./payments.page.scss'],
})
export class PaymentsPage implements OnInit {
  transactions$: Observable<any[]>;
  paymentMethods$: Observable<any[]>;
  errorMessage: string;
  selectedPaymentMethod: string;
  amount: number;

  constructor(private paymentService: PaymentService, private router: Router) {}

  ngOnInit(): void {
    this.loadTransactions();
    this.loadPaymentMethods();
  }

  // Load recent transactions
  loadTransactions(): void {
    this.transactions$ = this.paymentService.getTransactions().pipe(
      map((response) => response),
      catchError((error) => {
        this.errorMessage = 'Failed to load transactions.';
        return [];
      })
    );
  }

  // Load available payment methods
  loadPaymentMethods(): void {
    this.paymentMethods$ = this.paymentService.getPaymentMethods().pipe(
      map((response) => response),
      catchError((error) => {
        this.errorMessage = 'Failed to load payment methods.';
        return [];
      })
    );
  }

  // Select a payment method
  onPaymentMethodChange(paymentMethod: string): void {
    this.selectedPaymentMethod = paymentMethod;
  }

  // Process a new payment
  processPayment(): void {
    if (!this.selectedPaymentMethod || !this.amount) {
      this.errorMessage = 'Please select a payment method and enter an amount.';
      return;
    }

    this.paymentService
      .processPayment(this.selectedPaymentMethod, this.amount)
      .subscribe(
        (response) => {
          alert('Payment processed successfully!');
          this.loadTransactions();
        },
        (error) => {
          this.errorMessage = 'Payment failed. Please try again.';
        }
      );
  }

  // Retry a failed payment
  retryPayment(invoiceId: string): void {
    this.paymentService.retryInvoicePayment(invoiceId).subscribe(
      (response) => {
        alert('Payment retried successfully.');
        this.loadTransactions();
      },
      (error) => {
        this.errorMessage = 'Failed to retry payment.';
      }
    );
  }

  // Refund a payment
  refundPayment(paymentId: string): void {
    this.paymentService.refundPayment(paymentId).subscribe(
      (response) => {
        alert('Refund processed successfully.');
        this.loadTransactions();
      },
      (error) => {
        this.errorMessage = 'Refund failed. Please try again.';
      }
    );
  }

  // View transaction details
  viewTransactionDetails(transactionId: string): void {
    this.router.navigate([`/transactions/${transactionId}`]);
  }

  // Navigate to billing form
  navigateToBillingForm(): void {
    this.router.navigate(['/billing-form']);
  }

  // Fetch payment status
  getPaymentStatus(transactionId: string): void {
    this.paymentService.getPaymentStatus(transactionId).subscribe(
      (status) => {
        alert(`Payment status: ${status}`);
      },
      (error) => {
        this.errorMessage = 'Failed to retrieve payment status.';
      }
    );
  }

  // Fetch available currencies for making a payment
  loadAvailableCurrencies(): void {
    this.paymentService.getAvailableCurrencies().subscribe(
      (currencies) => {
        alert(`Available currencies: ${currencies.join(', ')}`);
      },
      (error) => {
        this.errorMessage = 'Failed to load available currencies.';
      }
    );
  }

  // Process payment for a specific invoice
  payInvoice(invoiceId: string, paymentMethodId: string): void {
    this.paymentService
      .processPayment(paymentMethodId, this.amount)
      .subscribe(
        (response) => {
          alert(`Invoice ${invoiceId} paid successfully!`);
          this.loadTransactions();
        },
        (error) => {
          this.errorMessage = `Failed to pay invoice ${invoiceId}.`;
        }
      );
  }

  // Cancel a pending payment
  cancelPayment(paymentId: string): void {
    if (confirm('Are you sure you want to cancel this payment?')) {
      this.paymentService.cancelSubscription(paymentId).subscribe(
        (response) => {
          alert('Payment canceled successfully.');
          this.loadTransactions();
        },
        (error) => {
          this.errorMessage = 'Failed to cancel payment.';
        }
      );
    }
  }

  // Generate a new invoice for the current user
  generateInvoice(): void {
    this.paymentService.generateInvoice('currentUserId').subscribe(
      (response) => {
        alert('Invoice generated successfully.');
        this.loadTransactions();
      },
      (error) => {
        this.errorMessage = 'Failed to generate invoice.';
      }
    );
  }

  // Helper to navigate to retrying payment for failed invoice
  retryInvoicePayment(invoiceId: string): void {
    this.paymentService.retryInvoicePayment(invoiceId).subscribe(
      (response) => {
        alert(`Payment for invoice ${invoiceId} retried successfully.`);
        this.loadTransactions();
      },
      (error) => {
        this.errorMessage = `Failed to retry payment for invoice ${invoiceId}.`;
      }
    );
  }

  // Navigate to transaction history page
  navigateToTransactionHistory(): void {
    this.router.navigate(['/transaction-history']);
  }

  // Helper function to refresh payments list
  refreshPayments(): void {
    this.loadTransactions();
  }

  // Error handling for payments
  private handlePaymentError(error: any): void {
    this.errorMessage = 'An error occurred with the payment service.';
  }

  // Retry payments in bulk for multiple failed invoices
  retryPaymentsInBulk(invoiceIds: string[]): void {
    invoiceIds.forEach((invoiceId) => {
      this.retryInvoicePayment(invoiceId);
    });
  }

  // Method to check if the amount entered is valid before processing payment
  isAmountValid(): boolean {
    return this.amount > 0;
  }

  // Handle the logic to update the amount when entering a new payment
  onAmountChange(amount: number): void {
    this.amount = amount;
  }

  // Navigate to a different page for manual billing details input
  goToManualBilling(): void {
    this.router.navigate(['/manual-billing']);
  }

  // View details for a specific failed transaction
  viewFailedTransactionDetails(transactionId: string): void {
    this.router.navigate([`/failed-transaction/${transactionId}`]);
  }

  // Retry payment for all failed invoices
  retryAllFailedPayments(): void {
    this.paymentService.getTransactions().subscribe(
      (transactions) => {
        const failedInvoices = transactions
          .filter((t) => t.status === 'failed')
          .map((t) => t.invoiceId);
        this.retryPaymentsInBulk(failedInvoices);
      },
      (error) => {
        this.errorMessage = 'Failed to load transactions.';
      }
    );
  }

  // Cancel all pending payments in bulk
  cancelAllPendingPayments(): void {
    if (confirm('Are you sure you want to cancel all pending payments?')) {
      this.paymentService.getTransactions().subscribe(
        (transactions) => {
          const pendingPayments = transactions
            .filter((t) => t.status === 'pending')
            .map((t) => t.paymentId);
          pendingPayments.forEach((paymentId) => {
            this.cancelPayment(paymentId);
          });
        },
        (error) => {
          this.errorMessage = 'Failed to load transactions.';
        }
      );
    }
  }
}