import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { PaymentService } from '../api/payment.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-billing-form',
  templateUrl: './billing-form.component.html',
  styleUrls: ['./billing-form.component.scss'],
})
export class BillingFormComponent implements OnInit {
  billingForm: FormGroup;
  submitted = false;
  paymentMethods: any[] = [];
  errorMessage: string;
  successMessage: string;

  constructor(
    private formBuilder: FormBuilder,
    private paymentService: PaymentService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Initialize the form with controls
    this.billingForm = this.formBuilder.group({
      fullName: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      address: ['', [Validators.required]],
      city: ['', [Validators.required]],
      state: ['', [Validators.required]],
      zipCode: ['', [Validators.required, Validators.pattern('^[0-9]{5}$')]],
      paymentMethod: ['', [Validators.required]],
      amount: [null, [Validators.required, Validators.min(1)]],
    });

    // Load payment methods
    this.loadPaymentMethods();
  }

  // Load payment methods from the backend API
  loadPaymentMethods(): void {
    this.paymentService.getPaymentMethods().subscribe(
      (methods) => {
        this.paymentMethods = methods;
      },
      (error) => {
        this.errorMessage = 'Failed to load payment methods.';
      }
    );
  }

  // Convenience getter for easy access to form fields
  get f() {
    return this.billingForm.controls;
  }

  // Handle form submission
  onSubmit(): void {
    this.submitted = true;

    // Stop here if form is invalid
    if (this.billingForm.invalid) {
      return;
    }

    // Prepare the payment data
    const paymentData = {
      fullName: this.f.fullName.value,
      email: this.f.email.value,
      address: this.f.address.value,
      city: this.f.city.value,
      state: this.f.state.value,
      zipCode: this.f.zipCode.value,
      paymentMethod: this.f.paymentMethod.value,
      amount: this.f.amount.value,
    };

    // Process the payment
    this.paymentService.processPayment(paymentData.paymentMethod, paymentData.amount).subscribe(
      (response) => {
        this.successMessage = 'Payment processed successfully!';
        this.resetForm();
        // Redirect to a success page or reload data
        this.router.navigate(['/payments']);
      },
      (error) => {
        this.errorMessage = 'Payment processing failed. Please try again.';
      }
    );
  }

  // Reset the form after successful submission
  resetForm(): void {
    this.submitted = false;
    this.billingForm.reset();
  }

  // Cancel the billing form and navigate back
  onCancel(): void {
    this.router.navigate(['/dashboard']);
  }

  // Method to handle validation error messages
  getErrorMessage(controlName: string): string {
    const control = this.billingForm.get(controlName);
    if (control?.hasError('required')) {
      return `${controlName} is required`;
    } else if (control?.hasError('minlength')) {
      return `${controlName} must be at least ${control?.errors?.minlength.requiredLength} characters`;
    } else if (control?.hasError('email')) {
      return 'Invalid email address';
    } else if (control?.hasError('pattern')) {
      return 'Invalid zip code';
    }
    return '';
  }
}