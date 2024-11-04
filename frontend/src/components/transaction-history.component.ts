import { Component, OnInit } from '@angular/core';
import { TransactionService } from '../api/transaction.service';
import { Transaction } from '../models/transaction.model';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-transaction-history',
  templateUrl: './transaction-history.component.html',
  styleUrls: ['./transaction-history.component.scss']
})
export class TransactionHistoryComponent implements OnInit {
  transactions$: Observable<Transaction[]>;
  currentPage: number = 1;
  totalItems: number = 0;
  itemsPerPage: number = 10;
  sortDirection: 'asc' | 'desc' = 'asc';
  sortField: string = 'date';

  constructor(private transactionService: TransactionService) {}

  ngOnInit(): void {
    this.loadTransactions();
  }

  loadTransactions(page: number = 1, sortField: string = 'date', sortDirection: string = 'asc'): void {
    this.transactions$ = this.transactionService.getTransactions(page, this.itemsPerPage, sortField, sortDirection);
    this.transactions$.subscribe(transactions => {
      this.totalItems = transactions.length;
    });
  }

  changePage(page: number): void {
    this.currentPage = page;
    this.loadTransactions(page, this.sortField, this.sortDirection);
  }

  changeSort(field: string): void {
    this.sortField = field;
    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    this.loadTransactions(this.currentPage, this.sortField, this.sortDirection);
  }

  formatAmount(amount: number): string {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  }

  formatDate(date: Date): string {
    return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: 'short', day: '2-digit' }).format(new Date(date));
  }

  trackById(index: number, transaction: Transaction): string {
    return transaction.id;
  }

  isTransactionPending(status: string): boolean {
    return status === 'Pending';
  }

  isTransactionFailed(status: string): boolean {
    return status === 'Failed';
  }

  isTransactionCompleted(status: string): boolean {
    return status === 'Completed';
  }

  reload(): void {
    this.loadTransactions(this.currentPage, this.sortField, this.sortDirection);
  }
}