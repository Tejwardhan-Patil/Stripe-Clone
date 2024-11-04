// Validate if the input is a valid email format
export function isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate if the input is a valid card number (Luhn Algorithm)
export function isValidCardNumber(cardNumber: string): boolean {
    const cleaned = cardNumber.replace(/\D/g, '');
    let sum = 0;
    let shouldDouble = false;
    for (let i = cleaned.length - 1; i >= 0; i--) {
        let digit = parseInt(cleaned.charAt(i), 10);
        if (shouldDouble) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        sum += digit;
        shouldDouble = !shouldDouble;
    }
    return sum % 10 === 0;
}

// Validate if the input is a valid CVV (3 or 4 digits)
export function isValidCVV(cvv: string, cardType: 'visa' | 'amex'): boolean {
    const cvvRegex = cardType === 'amex' ? /^\d{4}$/ : /^\d{3}$/;
    return cvvRegex.test(cvv);
}

// Validate if the expiration date is valid (MM/YY)
export function isValidExpiryDate(expiry: string): boolean {
    const [month, year] = expiry.split('/').map((part) => parseInt(part, 10));
    if (!month || !year || month < 1 || month > 12) return false;
    
    const currentDate = new Date();
    const expiryDate = new Date();
    expiryDate.setFullYear(2000 + year, month - 1);
    
    return expiryDate >= currentDate;
}

// Validate if the input is a valid postal code
export function isValidPostalCode(postalCode: string, countryCode: string): boolean {
    const postalCodeRegexes: { [key: string]: RegExp } = {
        US: /^\d{5}(-\d{4})?$/,
        CA: /^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$/,
        GB: /^[A-Z]{1,2}\d{1,2}[A-Z]? \d[A-Z]{2}$/,
        AU: /^\d{4}$/,
        FR: /^\d{5}$/,
        DE: /^\d{5}$/
    };
    const regex = postalCodeRegexes[countryCode];
    return regex ? regex.test(postalCode) : true; // Default to true for countries without regex
}

// Validate if the input is a valid phone number (International Format)
export function isValidPhoneNumber(phone: string): boolean {
    const phoneRegex = /^\+(?:[0-9] ?){6,14}[0-9]$/;
    return phoneRegex.test(phone);
}

// Validate if a string contains only alphabetic characters
export function isAlphabetic(input: string): boolean {
    return /^[a-zA-Z]+$/.test(input);
}

// Validate if a string contains only alphanumeric characters
export function isAlphanumeric(input: string): boolean {
    return /^[a-zA-Z0-9]+$/.test(input);
}

// Validate if the password meets complexity requirements
export function isValidPassword(password: string): boolean {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$/;
    return passwordRegex.test(password);
}

// Validate if two passwords match
export function passwordsMatch(password: string, confirmPassword: string): boolean {
    return password === confirmPassword;
}

// Validate a URL format
export function isValidURL(url: string): boolean {
    const urlRegex = /^(https?:\/\/)?([\w\d-]+)\.([a-z]{2,})(\/.*)?$/i;
    return urlRegex.test(url);
}

// Validate if the input is a valid tax ID (for US EIN)
export function isValidTaxID(taxId: string, countryCode: string): boolean {
    if (countryCode === 'US') {
        const einRegex = /^\d{2}-\d{7}$/;
        return einRegex.test(taxId);
    }
    return true;
}

// Validate if the input is a valid IBAN
export function isValidIBAN(iban: string): boolean {
    const ibanRegex = /^[A-Z]{2}\d{2}[A-Z\d]{1,30}$/;
    return ibanRegex.test(iban);
}

// Validate if the input is a valid SWIFT/BIC code
export function isValidSWIFTCode(swift: string): boolean {
    const swiftRegex = /^[A-Z]{4}[A-Z]{2}[A-Z\d]{2}([A-Z\d]{3})?$/;
    return swiftRegex.test(swift);
}

// Validate if the input is a valid account number (for US)
export function isValidAccountNumber(accountNumber: string): boolean {
    const accountNumberRegex = /^\d{9,12}$/;
    return accountNumberRegex.test(accountNumber);
}

// Validate if the input is a valid routing number (US-specific)
export function isValidRoutingNumber(routingNumber: string): boolean {
    const routingNumberRegex = /^\d{9}$/;
    return routingNumberRegex.test(routingNumber);
}

// Validate if a string is a valid cardholder name
export function isValidCardholderName(name: string): boolean {
    return /^[a-zA-Z\s]+$/.test(name);
}

// Validate if the input is a valid discount code
export function isValidDiscountCode(code: string): boolean {
    return /^[A-Z0-9]{6,10}$/.test(code);
}

// Validate if a transaction amount is valid (greater than zero)
export function isValidTransactionAmount(amount: number): boolean {
    return amount > 0;
}

// Validate a subscription interval (monthly, yearly)
export function isValidSubscriptionInterval(interval: string): boolean {
    const validIntervals = ['daily', 'weekly', 'monthly', 'yearly'];
    return validIntervals.includes(interval);
}

// Validate if a date is in the future
export function isFutureDate(date: string): boolean {
    const inputDate = new Date(date);
    return inputDate > new Date();
}

// Validate if the subscription end date is after the start date
export function isValidSubscriptionEndDate(startDate: string, endDate: string): boolean {
    return new Date(endDate) > new Date(startDate);
}

// Validate if the amount matches a given currency format (for USD)
export function isValidCurrencyAmount(amount: number, currencyCode: string): boolean {
    const decimalPlaces = { USD: 2, EUR: 2, JPY: 0 };
    const places = decimalPlaces[currencyCode] ?? 2;
    const factor = Math.pow(10, places);
    return Math.round(amount * factor) / factor === amount;
}