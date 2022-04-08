import { NgModule } from '@angular/core';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

// Imports for Angular Material components
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';

import { AppRoutingModule } from './app-routing.module';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { ConsoleComponent } from './console/console.component';
import { ErrorComponent } from './error/error.component';
import { LoginComponent } from './login/login.component';
import { PlaceComponent } from './place/place.component';
import { PlaceCreationDialogComponent } from './dialogs/place-creation-dialog/place-creation-dialog.component';
import { PlaceDeletionDialogComponent } from './dialogs/place-deletion-dialog/place-deletion-dialog.component';
import { PlaceOverviewComponent } from './place-overview/place-overview.component';
import { ResourceComponent } from './resource/resource.component';
import { ResourceOverviewComponent } from './resource-overview/resource-overview.component';
import { SidebarComponent } from './sidebar/sidebar.component';

import { ConsoleService } from './_services/console.service';
import { LoginService } from './auth/login.service';
import { PlaceService } from './_services/place.service';
import { ResourceService } from './_services/resource.service';

@NgModule({
    declarations: [
        AppComponent,
        ConsoleComponent,
        ErrorComponent,
        LoginComponent,
        PlaceComponent,
        PlaceCreationDialogComponent,
        PlaceDeletionDialogComponent,
        PlaceOverviewComponent,
        ResourceComponent,
        ResourceOverviewComponent,
        SidebarComponent,
    ],
    imports: [
        AppRoutingModule,
        BrowserModule,
        BrowserAnimationsModule,
        FormsModule,
        HttpClientModule,
        MatButtonModule,
        MatCardModule,
        MatDialogModule,
        MatDividerModule,
        MatFormFieldModule,
        MatIconModule,
        MatInputModule,
        MatPaginatorModule,
        MatSidenavModule,
        MatSnackBarModule,
        MatTableModule,
        MatToolbarModule,
        MatTooltipModule,
        RouterModule.forRoot([{ path: 'place', component: PlaceComponent }]),
    ],
    providers: [ConsoleService, LoginService, PlaceService, ResourceService],
    bootstrap: [AppComponent],
})
export class AppModule {}
