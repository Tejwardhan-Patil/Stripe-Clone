import { Component, OnInit } from '@angular/core';
import { SubscriptionService } from '../api/subscription.service';
import { Subscription } from '../models/subscription.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';

@Component({
  selector: 'app-subscriptions',
  templateUrl: './subscriptions.page.html',
  styleUrls: ['./subscriptions.page.scss'],
})
export class SubscriptionsPage implements OnInit {
  subscriptions: Subscription[] = [];
  isLoading: boolean = true;
  errorMessage: string = '';
  
  constructor(
    private subscriptionService: SubscriptionService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadSubscriptions();
  }

  // Method to load all subscriptions
  loadSubscriptions(): void {
    this.isLoading = true;
    this.subscriptionService.getSubscriptions().subscribe(
      (response: Subscription[]) => {
        this.subscriptions = response;
        this.isLoading = false;
      },
      (error) => {
        this.errorMessage = 'Failed to load subscriptions';
        this.snackBar.open(this.errorMessage, 'Close', { duration: 3000 });
        this.isLoading = false;
      }
    );
  }

  // Cancel a subscription
  cancelSubscription(subscriptionId: string): void {
    this.subscriptionService.cancelSubscription(subscriptionId).subscribe(
      () => {
        this.snackBar.open('Subscription canceled successfully', 'Close', { duration: 3000 });
        this.loadSubscriptions();
      },
      (error) => {
        this.snackBar.open('Failed to cancel subscription', 'Close', { duration: 3000 });
      }
    );
  }

  // Upgrade or downgrade subscription
  updateSubscription(subscriptionId: string, newPlanId: string): void {
    this.subscriptionService.updateSubscription(subscriptionId, newPlanId).subscribe(
      () => {
        this.snackBar.open('Subscription updated successfully', 'Close', { duration: 3000 });
        this.loadSubscriptions();
      },
      (error) => {
        this.snackBar.open('Failed to update subscription', 'Close', { duration: 3000 });
      }
    );
  }

  // Navigate to subscription details
  viewSubscriptionDetails(subscriptionId: string): void {
    this.router.navigate(['/subscriptions', subscriptionId]);
  }

  // Helper method to determine if subscription is active
  isSubscriptionActive(subscription: Subscription): boolean {
    return subscription.status === 'active';
  }

  // Helper method to format the subscription's end date
  formatEndDate(date: string): string {
    const endDate = new Date(date);
    return endDate.toLocaleDateString();
  }
}