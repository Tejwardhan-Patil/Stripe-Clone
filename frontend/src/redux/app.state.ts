import { ActionReducerMap, MetaReducer, Action } from '@ngrx/store';
import { createSelector, createFeatureSelector } from '@ngrx/store';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

// Define AppState interface
export interface AppState {
    payment: PaymentState;
    user: UserState;
    subscription: SubscriptionState;
}

// Define PaymentState interface
export interface PaymentState {
    paymentHistory: Payment[];
    selectedPayment: Payment | null;
    loading: boolean;
    error: string | null;
}

// Define UserState interface
export interface UserState {
    userDetails: UserDetails | null;
    isLoggedIn: boolean;
    loading: boolean;
    error: string | null;
}

// Define SubscriptionState interface
export interface SubscriptionState {
    subscriptions: Subscription[];
    activeSubscription: Subscription | null;
    loading: boolean;
    error: string | null;
}

// Payment, UserDetails, Subscription interfaces
export interface Payment {
    id: string;
    amount: number;
    date: string;
    status: string;
    method: string;
}

export interface UserDetails {
    id: string;
    name: string;
    email: string;
    role: string;
}

export interface Subscription {
    id: string;
    plan: string;
    status: string;
    startDate: string;
    endDate: string;
}

// Initial State Definitions
const initialPaymentState: PaymentState = {
    paymentHistory: [],
    selectedPayment: null,
    loading: false,
    error: null,
};

const initialUserState: UserState = {
    userDetails: null,
    isLoggedIn: false,
    loading: false,
    error: null,
};

const initialSubscriptionState: SubscriptionState = {
    subscriptions: [],
    activeSubscription: null,
    loading: false,
    error: null,
};

// Inlined Action Types and Action Classes for Payment
export enum PaymentActionTypes {
    LoadPaymentHistory = '[Payment] Load Payment History',
    LoadPaymentHistorySuccess = '[Payment] Load Payment History Success',
    LoadPaymentHistoryFailure = '[Payment] Load Payment History Failure',
}

export class LoadPaymentHistory implements Action {
    readonly type = PaymentActionTypes.LoadPaymentHistory;
}

export class LoadPaymentHistorySuccess implements Action {
    readonly type = PaymentActionTypes.LoadPaymentHistorySuccess;
    constructor(public payload: Payment[]) {}
}

export class LoadPaymentHistoryFailure implements Action {
    readonly type = PaymentActionTypes.LoadPaymentHistoryFailure;
    constructor(public payload: string) {}
}

export type PaymentActions = 
    | LoadPaymentHistory 
    | LoadPaymentHistorySuccess 
    | LoadPaymentHistoryFailure;

// Inlined Action Types and Action Classes for User
export enum UserActionTypes {
    LoadUserDetails = '[User] Load User Details',
    LoadUserDetailsSuccess = '[User] Load User Details Success',
    LoadUserDetailsFailure = '[User] Load User Details Failure',
}

export class LoadUserDetails implements Action {
    readonly type = UserActionTypes.LoadUserDetails;
}

export class LoadUserDetailsSuccess implements Action {
    readonly type = UserActionTypes.LoadUserDetailsSuccess;
    constructor(public payload: UserDetails) {}
}

export class LoadUserDetailsFailure implements Action {
    readonly type = UserActionTypes.LoadUserDetailsFailure;
    constructor(public payload: string) {}
}

export type UserActions = 
    | LoadUserDetails 
    | LoadUserDetailsSuccess 
    | LoadUserDetailsFailure;

// Inlined Action Types and Action Classes for Subscription
export enum SubscriptionActionTypes {
    LoadSubscriptions = '[Subscription] Load Subscriptions',
    LoadSubscriptionsSuccess = '[Subscription] Load Subscriptions Success',
    LoadSubscriptionsFailure = '[Subscription] Load Subscriptions Failure',
}

export class LoadSubscriptions implements Action {
    readonly type = SubscriptionActionTypes.LoadSubscriptions;
}

export class LoadSubscriptionsSuccess implements Action {
    readonly type = SubscriptionActionTypes.LoadSubscriptionsSuccess;
    constructor(public payload: Subscription[]) {}
}

export class LoadSubscriptionsFailure implements Action {
    readonly type = SubscriptionActionTypes.LoadSubscriptionsFailure;
    constructor(public payload: string) {}
}

export type SubscriptionActions = 
    | LoadSubscriptions 
    | LoadSubscriptionsSuccess 
    | LoadSubscriptionsFailure;

// Reducer for Payment State
export function paymentReducer(
    state = initialPaymentState,
    action: PaymentActions
): PaymentState {
    switch (action.type) {
        case PaymentActionTypes.LoadPaymentHistory:
            return { ...state, loading: true, error: null };
        case PaymentActionTypes.LoadPaymentHistorySuccess:
            return { ...state, loading: false, paymentHistory: action.payload };
        case PaymentActionTypes.LoadPaymentHistoryFailure:
            return { ...state, loading: false, error: action.payload };
        default:
            return state;
    }
}

// Reducer for User State
export function userReducer(
    state = initialUserState,
    action: UserActions
): UserState {
    switch (action.type) {
        case UserActionTypes.LoadUserDetails:
            return { ...state, loading: true, error: null };
        case UserActionTypes.LoadUserDetailsSuccess:
            return { ...state, loading: false, userDetails: action.payload, isLoggedIn: true };
        case UserActionTypes.LoadUserDetailsFailure:
            return { ...state, loading: false, error: action.payload };
        default:
            return state;
    }
}

// Reducer for Subscription State
export function subscriptionReducer(
    state = initialSubscriptionState,
    action: SubscriptionActions
): SubscriptionState {
    switch (action.type) {
        case SubscriptionActionTypes.LoadSubscriptions:
            return { ...state, loading: true, error: null };
        case SubscriptionActionTypes.LoadSubscriptionsSuccess:
            return { ...state, loading: false, subscriptions: action.payload };
        case SubscriptionActionTypes.LoadSubscriptionsFailure:
            return { ...state, loading: false, error: action.payload };
        default:
            return state;
    }
}

// Combine all reducers into an ActionReducerMap
export const reducers: ActionReducerMap<AppState> = {
    payment: paymentReducer,
    user: userReducer,
    subscription: subscriptionReducer,
};

// Meta reducers
export const metaReducers: MetaReducer<AppState>[] = !environment.production
    ? []
    : [];

// Selectors for PaymentState
export const selectPaymentState = createFeatureSelector<AppState, PaymentState>(
    'payment'
);
export const selectPaymentHistory = createSelector(
    selectPaymentState,
    (state: PaymentState) => state.paymentHistory
);
export const selectPaymentLoading = createSelector(
    selectPaymentState,
    (state: PaymentState) => state.loading
);
export const selectPaymentError = createSelector(
    selectPaymentState,
    (state: PaymentState) => state.error
);

// Selectors for UserState
export const selectUserState = createFeatureSelector<AppState, UserState>(
    'user'
);
export const selectUserDetails = createSelector(
    selectUserState,
    (state: UserState) => state.userDetails
);
export const selectIsLoggedIn = createSelector(
    selectUserState,
    (state: UserState) => state.isLoggedIn
);
export const selectUserLoading = createSelector(
    selectUserState,
    (state: UserState) => state.loading
);
export const selectUserError = createSelector(
    selectUserState,
    (state: UserState) => state.error
);

// Selectors for SubscriptionState
export const selectSubscriptionState = createFeatureSelector<AppState, SubscriptionState>(
    'subscription'
);
export const selectSubscriptions = createSelector(
    selectSubscriptionState,
    (state: SubscriptionState) => state.subscriptions
);
export const selectActiveSubscription = createSelector(
    selectSubscriptionState,
    (state: SubscriptionState) => state.activeSubscription
);
export const selectSubscriptionLoading = createSelector(
    selectSubscriptionState,
    (state: SubscriptionState) => state.loading
);
export const selectSubscriptionError = createSelector(
    selectSubscriptionState,
    (state: SubscriptionState) => state.error
);

// Export the AppState as an observable
export const selectAppState = (state: AppState): Observable<AppState> =>
    new Observable((observer) => {
        observer.next(state);
        observer.complete();
    });