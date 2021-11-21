import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';

import { PlaceService } from '../services/place.service';
import { Place } from '../../models/place';
import { ResourceService } from '../services/resource.service';
import { Resource } from '../../models/resource';

@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.css']
})
export class PlaceComponent implements OnInit {

  place: Place = new Place('', false, '','',[]);
  resources: Resource[] = [];

  constructor(private _ps: PlaceService, private _rs: ResourceService, private route: ActivatedRoute, private router: Router) {
    route.params.subscribe(val => {
      const currentRoute = route.snapshot.url[route.snapshot.url.length-1].path;
      this._ps.getPlace(currentRoute).then(data => {
        this.place = data;
        this.getResources();
      });
    })
  }

  ngOnInit(): void {

  }

  private getResources(): void {
    this._rs.getResourcesForPlace(this.place.name).then(resources => {
      this.resources = resources;
    });
  }

  public navigateToResource(resourceName: string) {
    this.router.navigate(['resource/', resourceName]);
  }

}
