import { Injectable } from '@angular/core';

// Define supported currency codes
export enum CurrencyCode {
    USD = 'USD',
    EUR = 'EUR',
    GBP = 'GBP',
    JPY = 'JPY',
    CAD = 'CAD',
    AUD = 'AUD',
    INR = 'INR',
    CNY = 'CNY',
    BRL = 'BRL',
    ZAR = 'ZAR',
}

// Define currency symbols
const CurrencySymbols: { [key in CurrencyCode]: string } = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    CAD: 'C$',
    AUD: 'A$',
    INR: '₹',
    CNY: '¥',
    BRL: 'R$',
    ZAR: 'R',
};

// Configuration for formatting options
export interface CurrencyFormatOptions {
    locale?: string; // Locale for number formatting
    useGrouping?: boolean; // Whether to group numbers (1,000)
    decimalPlaces?: number; // Number of decimal places
    currencySymbol?: string; // Override the default currency symbol
}

// Default formatting options
const defaultOptions: CurrencyFormatOptions = {
    locale: 'en-US',
    useGrouping: true,
    decimalPlaces: 2,
};

// Currency formatter class
@Injectable({
    providedIn: 'root',
})
export class CurrencyFormatter {

    // Main function to format amounts
    format(
        amount: number,
        currency: CurrencyCode,
        options: CurrencyFormatOptions = defaultOptions
    ): string {
        const opts = { ...defaultOptions, ...options };

        const formattedAmount = new Intl.NumberFormat(opts.locale, {
            style: 'currency',
            currency: currency,
            useGrouping: opts.useGrouping,
            minimumFractionDigits: opts.decimalPlaces,
            maximumFractionDigits: opts.decimalPlaces,
        }).format(amount);

        return formattedAmount;
    }

    // Get the currency symbol
    getCurrencySymbol(currency: CurrencyCode): string {
        return CurrencySymbols[currency] || '';
    }

    // Helper to format with custom symbol
    formatWithCustomSymbol(
        amount: number,
        symbol: string,
        options: CurrencyFormatOptions = defaultOptions
    ): string {
        const opts = { ...defaultOptions, ...options };

        const formattedAmount = new Intl.NumberFormat(opts.locale, {
            useGrouping: opts.useGrouping,
            minimumFractionDigits: opts.decimalPlaces,
            maximumFractionDigits: opts.decimalPlaces,
        }).format(amount);

        return `${symbol}${formattedAmount}`;
    }

    // Convert amount from one currency to another using exchange rate
    convertAmount(
        amount: number,
        fromCurrency: CurrencyCode,
        toCurrency: CurrencyCode,
        exchangeRate: number,
        options: CurrencyFormatOptions = defaultOptions
    ): string {
        const convertedAmount = amount * exchangeRate;
        return this.format(convertedAmount, toCurrency, options);
    }

    // Format for percentage displays
    formatAsPercentage(
        amount: number,
        decimalPlaces: number = 2
    ): string {
        return `${(amount * 100).toFixed(decimalPlaces)}%`;
    }

    // Parse formatted currency back to number
    parseCurrency(formattedCurrency: string): number {
        const unformatted = formattedCurrency.replace(/[^\d.-]/g, '');
        return parseFloat(unformatted);
    }

    // Add a method for rounding currency
    roundCurrency(amount: number, decimalPlaces: number = 2): number {
        const factor = Math.pow(10, decimalPlaces);
        return Math.round(amount * factor) / factor;
    }

    // Handle large amounts in a human-readable format ($1M, $2B)
    formatLargeAmount(
        amount: number,
        currency: CurrencyCode,
        options: CurrencyFormatOptions = defaultOptions
    ): string {
        const opts = { ...defaultOptions, ...options };

        let suffix = '';
        let value = amount;

        if (Math.abs(amount) >= 1.0e9) {
            value = amount / 1.0e9;
            suffix = 'B';
        } else if (Math.abs(amount) >= 1.0e6) {
            value = amount / 1.0e6;
            suffix = 'M';
        } else if (Math.abs(amount) >= 1.0e3) {
            value = amount / 1.0e3;
            suffix = 'K';
        }

        const formattedAmount = new Intl.NumberFormat(opts.locale, {
            useGrouping: opts.useGrouping,
            minimumFractionDigits: opts.decimalPlaces,
            maximumFractionDigits: opts.decimalPlaces,
        }).format(value);

        return `${this.getCurrencySymbol(currency)}${formattedAmount}${suffix}`;
    }

    // Get a list of all supported currencies
    getSupportedCurrencies(): CurrencyCode[] {
        return Object.keys(CurrencySymbols) as CurrencyCode[];
    }

    // Custom function to handle negative amounts (refunds)
    formatNegativeAmount(
        amount: number,
        currency: CurrencyCode,
        options: CurrencyFormatOptions = defaultOptions
    ): string {
        const formattedAmount = this.format(Math.abs(amount), currency, options);
        return `-${formattedAmount}`;
    }

    // Utility to add/subtract currency values safely
    addAmounts(
        amount1: number,
        amount2: number
    ): number {
        return this.roundCurrency(amount1 + amount2);
    }

    subtractAmounts(
        amount1: number,
        amount2: number
    ): number {
        return this.roundCurrency(amount1 - amount2);
    }

    // Format for cryptocurrency values (BTC, ETH)
    formatForCrypto(
        amount: number,
        decimalPlaces: number = 8
    ): string {
        return `${amount.toFixed(decimalPlaces)} BTC`;
    }
    
    // Handle currencies with no decimal places (JPY)
    formatZeroDecimalCurrency(
        amount: number,
        currency: CurrencyCode
    ): string {
        const opts: CurrencyFormatOptions = { ...defaultOptions, decimalPlaces: 0 };
        return this.format(amount, currency, opts);
    }

    // Extend formatting for right-to-left languages
    formatForRTL(
        amount: number,
        currency: CurrencyCode,
        options: CurrencyFormatOptions = { locale: 'ar-EG' }
    ): string {
        return this.format(amount, currency, options);
    }
}

// Usage in component
// import { CurrencyFormatter, CurrencyCode } from 'src/utils/currency-formatter.ts';

// let formatter = new CurrencyFormatter();
// console.log(formatter.format(1000, CurrencyCode.USD)); // $1,000.00