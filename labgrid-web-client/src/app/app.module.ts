import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';

// Import of Angular Material components
import { MatIconModule } from '@angular/material/icon'
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatCardModule} from '@angular/material/card';
import {MatButtonModule} from '@angular/material/button';
import {MatDividerModule} from '@angular/material/divider';

import { AppComponent } from './app.component';
import { ErrorComponent } from './error/error.component';
import { SidebarComponent } from './sidebar/sidebar.component';
import { WelcomeComponent } from './welcome/welcome.component';

import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { PlaceService } from './place.service';
import { PlaceComponent } from './place/place.component';
import { RouterModule } from '@angular/router';

@NgModule({
  declarations: [
    AppComponent,
    SidebarComponent,
    WelcomeComponent,
    ErrorComponent,
    PlaceComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatIconModule,
    MatSidenavModule,
    MatToolbarModule,
    MatCardModule,
    MatButtonModule,
    MatDividerModule,
    RouterModule.forRoot([
      {path: "place", component: PlaceComponent}
    ])
  ],
  providers: [
    PlaceService
  ],
  bootstrap: [
    AppComponent
  ]
})
export class AppModule { }
