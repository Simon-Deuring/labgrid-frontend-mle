import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';

// Import of Angular Material components
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { AppComponent } from './app.component';
import { ErrorComponent } from './error/error.component';
import { SidebarComponent } from './sidebar/sidebar.component';

import { RouterModule } from '@angular/router';
import { AppRoutingModule } from './app-routing.module';

import { PlaceService } from './_services/place.service';
import { PlaceComponent } from './place/place.component';
import { ResourceService } from './_services/resource.service';
import { ResourceComponent } from './resource/resource.component';
import { ResourceOverviewComponent } from './resource-overview/resource-overview.component';
import { PlaceOverviewComponent } from './place-overview/place-overview.component';
import { HttpClientModule } from '@angular/common/http';

@NgModule({
    declarations: [
        AppComponent,
        SidebarComponent,
        ErrorComponent,
        PlaceComponent,
        ResourceComponent,
        ResourceOverviewComponent,
        PlaceOverviewComponent,
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
        MatTableModule,
        MatPaginatorModule,
        MatFormFieldModule,
        MatInputModule,
        MatSnackBarModule,
        RouterModule.forRoot([{ path: 'place', component: PlaceComponent }]),
    ],
    providers: [PlaceService, ResourceService],
    bootstrap: [AppComponent],
})
export class AppModule {}
