import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ErrorComponent } from './error/error.component';
import { LoginComponent } from './login/login.component';
import { PlaceComponent } from './place/place.component';
import { PlaceOverviewComponent } from './place-overview/place-overview.component';
import { ResourceComponent } from './resource/resource.component';
import { ResourceOverviewComponent } from './resource-overview/resource-overview.component';

const routes: Routes = [
    { path: '', component: PlaceOverviewComponent },
    { path: 'place/:placename', component: PlaceComponent },
    { path: 'resourceOverview', component: ResourceOverviewComponent },
    { path: 'resource/:resourceName', component: ResourceComponent },
    { path: 'login', component: LoginComponent },
    { path: '**', component: ErrorComponent },
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule],
})
export class AppRoutingModule {}
