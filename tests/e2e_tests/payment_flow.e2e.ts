import { test, expect } from '@playwright/test';

test.describe('Payment Flow E2E Test', () => {
  
  // Before each test, log in as a valid user
  test.beforeEach(async ({ page }) => {
    await page.goto('https://website.com/login');
    await page.fill('input[name="email"]', 'validuser@website.com');
    await page.fill('input[name="password"]', 'ValidPassword123');
    await page.click('button[type="submit"]');
    await page.waitForURL('https://website.com/dashboard');
  });

  test('User can add a valid credit card and complete a payment', async ({ page }) => {
    // Navigate to the payments page
    await page.goto('https://website.com/payments');
    await page.waitForSelector('text=Billing Information');
    
    // Fill in billing form
    await page.fill('input[name="fullName"]', 'Person');
    await page.fill('input[name="address"]', '123 Payment St.');
    await page.fill('input[name="city"]', 'Paytown');
    await page.fill('input[name="postalCode"]', '12345');
    await page.selectOption('select[name="country"]', 'US');
    
    // Enter card details
    await page.fill('input[name="cardNumber"]', '4242424242424242');
    await page.fill('input[name="expiryDate"]', '12/25');
    await page.fill('input[name="cvc"]', '123');
    
    // Submit payment form
    await page.click('button[type="submit"]');
    
    // Expect success notification
    await page.waitForSelector('text=Payment successful');
    const successMessage = await page.$eval('.notification', el => el.textContent);
    expect(successMessage).toBe('Payment successful');
  });

  test('User cannot add an invalid credit card', async ({ page }) => {
    // Navigate to the payments page
    await page.goto('https://website.com/payments');
    await page.waitForSelector('text=Billing Information');
    
    // Fill in billing form with valid data
    await page.fill('input[name="fullName"]', 'Person');
    await page.fill('input[name="address"]', '123 Payment St.');
    await page.fill('input[name="city"]', 'Paytown');
    await page.fill('input[name="postalCode"]', '12345');
    await page.selectOption('select[name="country"]', 'US');
    
    // Enter invalid card details
    await page.fill('input[name="cardNumber"]', '4000000000000002');
    await page.fill('input[name="expiryDate"]', '12/25');
    await page.fill('input[name="cvc"]', '123');
    
    // Submit payment form
    await page.click('button[type="submit"]');
    
    // Expect failure notification
    await page.waitForSelector('text=Payment failed');
    const failureMessage = await page.$eval('.notification', el => el.textContent);
    expect(failureMessage).toBe('Payment failed: Invalid card number');
  });

  test('User can view transaction history after payment', async ({ page }) => {
    // Navigate to the transaction history page
    await page.goto('https://website.com/transaction-history');
    
    // Ensure that at least one transaction exists
    const transactions = await page.$$eval('.transaction-row', rows => rows.length);
    expect(transactions).toBeGreaterThan(0);
    
    // Verify transaction details
    const transactionAmount = await page.$eval('.transaction-row:first-child .amount', el => el.textContent);
    expect(transactionAmount).toBe('$100.00');
    
    const transactionStatus = await page.$eval('.transaction-row:first-child .status', el => el.textContent);
    expect(transactionStatus).toBe('Completed');
  });

  test('Subscription payment flow works correctly', async ({ page }) => {
    // Navigate to the subscription page
    await page.goto('https://website.com/subscriptions');
    await page.waitForSelector('text=Subscription Plans');
    
    // Select a subscription plan
    await page.click('.plan-card[data-plan-id="premium"] button');
    
    // Fill in billing information
    await page.fill('input[name="fullName"]', 'Person');
    await page.fill('input[name="address"]', '123 Subscription St.');
    await page.fill('input[name="city"]', 'Subtown');
    await page.fill('input[name="postalCode"]', '67890');
    await page.selectOption('select[name="country"]', 'US');
    
    // Enter valid card details
    await page.fill('input[name="cardNumber"]', '4242424242424242');
    await page.fill('input[name="expiryDate"]', '12/25');
    await page.fill('input[name="cvc"]', '123');
    
    // Submit subscription payment
    await page.click('button[type="submit"]');
    
    // Expect success notification
    await page.waitForSelector('text=Subscription successful');
    const subscriptionSuccessMessage = await page.$eval('.notification', el => el.textContent);
    expect(subscriptionSuccessMessage).toBe('Subscription successful');
  });

  test('Refund request flow works correctly', async ({ page }) => {
    // Navigate to the transaction history page
    await page.goto('https://website.com/transaction-history');
    
    // Request refund for a transaction
    await page.click('.transaction-row:first-child .refund-button');
    await page.waitForSelector('text=Refund Requested');
    
    // Verify refund request message
    const refundMessage = await page.$eval('.notification', el => el.textContent);
    expect(refundMessage).toBe('Refund requested successfully');
    
    // Verify status change in transaction history
    const transactionStatus = await page.$eval('.transaction-row:first-child .status', el => el.textContent);
    expect(transactionStatus).toBe('Refund Pending');
  });

  test('User cannot proceed with an expired card', async ({ page }) => {
    // Navigate to the payments page
    await page.goto('https://website.com/payments');
    
    // Fill in billing information
    await page.fill('input[name="fullName"]', 'Person');
    await page.fill('input[name="address"]', '456 Expiry St.');
    await page.fill('input[name="city"]', 'ExpiredCity');
    await page.fill('input[name="postalCode"]', '98765');
    await page.selectOption('select[name="country"]', 'US');
    
    // Enter expired card details
    await page.fill('input[name="cardNumber"]', '4000000000000069');
    await page.fill('input[name="expiryDate"]', '01/22');
    await page.fill('input[name="cvc"]', '123');
    
    // Submit payment form
    await page.click('button[type="submit"]');
    
    // Expect failure notification
    await page.waitForSelector('text=Payment failed');
    const failureMessage = await page.$eval('.notification', el => el.textContent);
    expect(failureMessage).toBe('Payment failed: Expired card');
  });

});