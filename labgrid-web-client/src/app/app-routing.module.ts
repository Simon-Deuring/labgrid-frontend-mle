import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ErrorComponent } from './error/error.component';
import { PlaceComponent } from './place/place.component';
import { ResourceComponent } from './resource/resource.component';
import { ResourceOverviewComponent } from './resource-overview/resource-overview.component';
import { WelcomeComponent } from './welcome/welcome.component';

const routes: Routes = [
  { path: '', component: WelcomeComponent },
  { path: 'place/:placename', component: PlaceComponent},
  { path: 'resourceOverview', component: ResourceOverviewComponent},
  { path: 'resource/:resourceName', component: ResourceComponent},
  { path: '**', component: ErrorComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
