import { createAction, props } from '@ngrx/store';

// Define payment action types
export const LOAD_TRANSACTIONS = '[Payment] Load Transactions';
export const LOAD_TRANSACTIONS_SUCCESS = '[Payment] Load Transactions Success';
export const LOAD_TRANSACTIONS_FAILURE = '[Payment] Load Transactions Failure';

export const PROCESS_PAYMENT = '[Payment] Process Payment';
export const PROCESS_PAYMENT_SUCCESS = '[Payment] Process Payment Success';
export const PROCESS_PAYMENT_FAILURE = '[Payment] Process Payment Failure';

export const REFUND_PAYMENT = '[Payment] Refund Payment';
export const REFUND_PAYMENT_SUCCESS = '[Payment] Refund Payment Success';
export const REFUND_PAYMENT_FAILURE = '[Payment] Refund Payment Failure';

export const RETRY_PAYMENT = '[Payment] Retry Payment';
export const RETRY_PAYMENT_SUCCESS = '[Payment] Retry Payment Success';
export const RETRY_PAYMENT_FAILURE = '[Payment] Retry Payment Failure';

export const LOAD_PAYMENT_METHODS = '[Payment] Load Payment Methods';
export const LOAD_PAYMENT_METHODS_SUCCESS = '[Payment] Load Payment Methods Success';
export const LOAD_PAYMENT_METHODS_FAILURE = '[Payment] Load Payment Methods Failure';

export const LOAD_PAYMENT_STATUS = '[Payment] Load Payment Status';
export const LOAD_PAYMENT_STATUS_SUCCESS = '[Payment] Load Payment Status Success';
export const LOAD_PAYMENT_STATUS_FAILURE = '[Payment] Load Payment Status Failure';

// Load transactions action
export const loadTransactions = createAction(LOAD_TRANSACTIONS);

export const loadTransactionsSuccess = createAction(
  LOAD_TRANSACTIONS_SUCCESS,
  props<{ transactions: any[] }>()
);

export const loadTransactionsFailure = createAction(
  LOAD_TRANSACTIONS_FAILURE,
  props<{ error: string }>()
);

// Process payment actions
export const processPayment = createAction(
  PROCESS_PAYMENT,
  props<{ paymentMethodId: string; amount: number }>()
);

export const processPaymentSuccess = createAction(
  PROCESS_PAYMENT_SUCCESS,
  props<{ payment: any }>()
);

export const processPaymentFailure = createAction(
  PROCESS_PAYMENT_FAILURE,
  props<{ error: string }>()
);

// Refund payment actions
export const refundPayment = createAction(
  REFUND_PAYMENT,
  props<{ paymentId: string }>()
);

export const refundPaymentSuccess = createAction(
  REFUND_PAYMENT_SUCCESS,
  props<{ refund: any }>()
);

export const refundPaymentFailure = createAction(
  REFUND_PAYMENT_FAILURE,
  props<{ error: string }>()
);

// Retry payment actions
export const retryPayment = createAction(
  RETRY_PAYMENT,
  props<{ invoiceId: string }>()
);

export const retryPaymentSuccess = createAction(
  RETRY_PAYMENT_SUCCESS,
  props<{ payment: any }>()
);

export const retryPaymentFailure = createAction(
  RETRY_PAYMENT_FAILURE,
  props<{ error: string }>()
);

// Load available payment methods
export const loadPaymentMethods = createAction(LOAD_PAYMENT_METHODS);

export const loadPaymentMethodsSuccess = createAction(
  LOAD_PAYMENT_METHODS_SUCCESS,
  props<{ paymentMethods: any[] }>()
);

export const loadPaymentMethodsFailure = createAction(
  LOAD_PAYMENT_METHODS_FAILURE,
  props<{ error: string }>()
);

// Load payment status actions
export const loadPaymentStatus = createAction(
  LOAD_PAYMENT_STATUS,
  props<{ transactionId: string }>()
);

export const loadPaymentStatusSuccess = createAction(
  LOAD_PAYMENT_STATUS_SUCCESS,
  props<{ status: string }>()
);

export const loadPaymentStatusFailure = createAction(
  LOAD_PAYMENT_STATUS_FAILURE,
  props<{ error: string }>()
);

// Reset payment state action
export const resetPaymentState = createAction('[Payment] Reset Payment State');