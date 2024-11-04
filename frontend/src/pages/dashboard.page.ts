import { Component, OnInit } from '@angular/core';
import { PaymentService } from '../api/payment.service';
import { SubscriptionService } from '../api/subscription.service';
import { Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { Chart } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.page.html',
  styleUrls: ['./dashboard.page.scss'],
})
export class DashboardPage implements OnInit {
  transactions$: Observable<any[]>;
  subscriptionStatus$: Observable<any>;
  revenueChart: any;
  paymentMethods$: Observable<any[]>;
  subscriptionPlans$: Observable<any[]>;
  errorMessage: string;

  constructor(
    private paymentService: PaymentService,
    private subscriptionService: SubscriptionService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadTransactions();
    this.loadSubscriptionStatus();
    this.loadPaymentMethods();
    this.loadSubscriptionPlans();
    this.generateRevenueChart();
  }

  // Load recent payment transactions
  loadTransactions(): void {
    this.transactions$ = this.paymentService.getTransactions().pipe(
      map((data) => data),
      catchError((error) => {
        this.errorMessage = error;
        return [];
      })
    );
  }

  // Load subscription status
  loadSubscriptionStatus(): void {
    this.subscriptionStatus$ = this.subscriptionService.getUserSubscriptionStatus('currentUserId').pipe(
      map((data) => data),
      catchError((error) => {
        this.errorMessage = error;
        return [];
      })
    );
  }

  // Load available payment methods
  loadPaymentMethods(): void {
    this.paymentMethods$ = this.paymentService.getPaymentMethods().pipe(
      map((data) => data),
      catchError((error) => {
        this.errorMessage = error;
        return [];
      })
    );
  }

  // Load subscription plans available for the user
  loadSubscriptionPlans(): void {
    this.subscriptionPlans$ = this.subscriptionService.getSubscriptionPlans().pipe(
      map((data) => data),
      catchError((error) => {
        this.errorMessage = error;
        return [];
      })
    );
  }

  // Handle the logic for navigating to detailed transaction pages
  viewTransactionDetail(transactionId: string): void {
    this.router.navigate([`/transactions/${transactionId}`]);
  }

  // Handle the logic for subscribing to a new plan
  subscribeToPlan(planId: string): void {
    this.subscriptionService.subscribeToPlan(planId, 'currentUserId').subscribe(
      (response) => {
        alert('Subscription successful');
        this.loadSubscriptionStatus();
      },
      (error) => {
        this.errorMessage = 'Failed to subscribe to the plan.';
      }
    );
  }

  // Render a revenue chart for visualization
  generateRevenueChart(): void {
    this.paymentService.getTransactions().subscribe((transactions) => {
      const transactionDates = transactions.map((t) => t.date);
      const transactionAmounts = transactions.map((t) => t.amount);

      this.revenueChart = new Chart('revenueChart', {
        type: 'line',
        data: {
          labels: transactionDates,
          datasets: [
            {
              label: 'Revenue over Time',
              data: transactionAmounts,
              borderColor: 'rgba(75, 192, 192, 1)',
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: {
              type: 'time',
              time: {
                unit: 'month',
              },
            },
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    });
  }

  // Refresh the data on the dashboard manually
  refreshDashboard(): void {
    this.loadTransactions();
    this.loadSubscriptionStatus();
    this.loadPaymentMethods();
    this.loadSubscriptionPlans();
  }

  // Cancel a subscription
  cancelSubscription(subscriptionId: string): void {
    this.subscriptionService.cancelSubscription(subscriptionId).subscribe(
      (response) => {
        alert('Subscription canceled successfully.');
        this.loadSubscriptionStatus();
      },
      (error) => {
        this.errorMessage = 'Failed to cancel subscription.';
      }
    );
  }

  // Retry a payment for a failed invoice
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

  // Navigate to the billing form page
  navigateToBillingForm(): void {
    this.router.navigate(['/billing-form']);
  }

  // Show subscription details
  viewSubscriptionDetails(subscriptionId: string): void {
    this.router.navigate([`/subscriptions/${subscriptionId}`]);
  }

  // Error handling function
  private handleError(error: any): void {
    this.errorMessage = 'An error occurred. Please try again later.';
  }
}