import { enableProdMode } from '@angular/core';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';

import { AppModule } from './app.module';
import { environment } from './environments/environment';

// Check if the app is running in production mode, and enable production mode if true
if (environment.production) {
  enableProdMode();
}

// Bootstrap the Angular application with the AppModule
platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .catch((err) => console.error(err));