import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginGuard } from './auth/login.guard';

import { ErrorComponent } from './error/error.component';
import { LoginComponent } from './login/login.component';
import { PlaceComponent } from './place/place.component';
import { PlaceOverviewComponent } from './place-overview/place-overview.component';
import { ResourceComponent } from './resource/resource.component';
import { ResourceOverviewComponent } from './resource-overview/resource-overview.component';
import { ChartComponent } from './chart/chart.component';

const routes: Routes = [
    { path: '', component: PlaceOverviewComponent, canActivate: [LoginGuard] },
    { path: 'dashboard', component: ChartComponent, canActivate: [LoginGuard] },
    { path: 'place/:placename', component: PlaceComponent, canActivate: [LoginGuard] },
    { path: 'resourceOverview', component: ResourceOverviewComponent, canActivate: [LoginGuard] },
    { path: 'resource/:resourceName', component: ResourceComponent, canActivate: [LoginGuard] },
    { path: 'login', component: LoginComponent },
    { path: '**', component: ErrorComponent, canActivate: [LoginGuard] },
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule],
})
export class AppRoutingModule {}
