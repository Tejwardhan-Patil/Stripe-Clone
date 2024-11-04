import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class PaymentService {
  private apiUrl = 'https://api.website.com/payments';
  private headers = new HttpHeaders({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${this.getToken()}`,
  });

  constructor(private http: HttpClient) {}

  // Handle errors from HTTP calls
  private handleError(error: any): Observable<never> {
    let errorMessage = '';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Client-side error: ${error.error.message}`;
    } else {
      errorMessage = `Server-side error: ${error.status} ${error.message}`;
    }
    return throwError(errorMessage);
  }

  // Get the token from localStorage or other secure storage
  private getToken(): string {
    return localStorage.getItem('access_token') || '';
  }

  // Fetch all payment transactions
  getTransactions(): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/transactions`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Get a single payment transaction by ID
  getTransactionById(id: string): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/transactions/${id}`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Create a new payment
  createPayment(paymentData: any): Observable<any> {
    return this.http
      .post(`${this.apiUrl}/create`, paymentData, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  // Update an existing payment
  updatePayment(id: string, paymentData: any): Observable<any> {
    return this.http
      .put(`${this.apiUrl}/update/${id}`, paymentData, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  // Delete a payment by ID
  deletePayment(id: string): Observable<any> {
    return this.http
      .delete(`${this.apiUrl}/delete/${id}`, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  // Fetch available payment methods
  getPaymentMethods(): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/methods`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Process a payment using a selected payment method
  processPayment(paymentMethodId: string, amount: number): Observable<any> {
    const paymentData = { method_id: paymentMethodId, amount: amount };
    return this.http
      .post(`${this.apiUrl}/process`, paymentData, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  // Fetch the available currencies for payments
  getAvailableCurrencies(): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/currencies`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Refund a payment by ID
  refundPayment(paymentId: string): Observable<any> {
    return this.http
      .post(`${this.apiUrl}/refund/${paymentId}`, null, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  // Fetch the refund status by refund ID
  getRefundStatus(refundId: string): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/refund/status/${refundId}`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Webhook verification for payment events
  verifyWebhookSignature(signature: string, payload: any): Observable<any> {
    const body = { signature, payload };
    return this.http
      .post(`${this.apiUrl}/webhook/verify`, body, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  // Helper to fetch the payment status for a transaction
  getPaymentStatus(transactionId: string): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/status/${transactionId}`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Fetch recurring payment plans
  getSubscriptionPlans(): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/subscriptions/plans`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Subscribe user to a plan
  subscribeToPlan(planId: string, userId: string): Observable<any> {
    const subscriptionData = { plan_id: planId, user_id: userId };
    return this.http
      .post(`${this.apiUrl}/subscriptions/subscribe`, subscriptionData, {
        headers: this.headers,
      })
      .pipe(catchError(this.handleError));
  }

  // Cancel subscription by subscription ID
  cancelSubscription(subscriptionId: string): Observable<any> {
    return this.http
      .post(
        `${this.apiUrl}/subscriptions/cancel/${subscriptionId}`,
        null,
        { headers: this.headers }
      )
      .pipe(catchError(this.handleError));
  }

  // Fetch user's subscription status
  getUserSubscriptionStatus(userId: string): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/subscriptions/status/${userId}`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Fetch all past invoices for a user
  getInvoices(userId: string): Observable<any> {
    return this.http
      .get(`${this.apiUrl}/invoices/${userId}`, { headers: this.headers })
      .pipe(
        map((response: any) => response.data),
        catchError(this.handleError)
      );
  }

  // Generate a new invoice for a user
  generateInvoice(userId: string): Observable<any> {
    return this.http
      .post(`${this.apiUrl}/invoices/generate/${userId}`, null, {
        headers: this.headers,
      })
      .pipe(catchError(this.handleError));
  }

  // Retry failed payment for an invoice
  retryInvoicePayment(invoiceId: string): Observable<any> {
    return this.http
      .post(`${this.apiUrl}/invoices/retry/${invoiceId}`, null, {
        headers: this.headers,
      })
      .pipe(catchError(this.handleError));
  }
}