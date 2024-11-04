import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';

import { AppComponent } from './app.component';
import { DashboardPage } from './pages/dashboard.page';
import { PaymentsPage } from './pages/payments.page';
import { BillingFormComponent } from './components/billing-form.component';
import { TransactionHistoryComponent } from './components/transaction-history.component';
import { environment } from '../environments/environment';

import { reducers, metaReducers } from './redux/reducers';
import { PaymentEffects } from './redux/payment.effects';

// Importing Angular Material modules
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';

@NgModule({
  declarations: [
    AppComponent,
    DashboardPage,
    PaymentsPage,
    BillingFormComponent,
    TransactionHistoryComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    ReactiveFormsModule,
    FormsModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    StoreModule.forRoot(reducers, { metaReducers }),
    EffectsModule.forRoot([PaymentEffects]),
    StoreDevtoolsModule.instrument({ maxAge: 25, logOnly: environment.production }),

    // Angular Material Modules
    MatButtonModule,
    MatInputModule,
    MatSelectModule,
    MatCardModule,
    MatToolbarModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}