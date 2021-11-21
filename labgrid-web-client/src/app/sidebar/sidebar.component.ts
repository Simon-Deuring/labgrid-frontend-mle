import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { PlaceService } from '../_services/place.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {

  public places: any = [];

  constructor(private _ps: PlaceService, private router: Router) { }

  ngOnInit(): void {
    this._ps.getPlaces()
      .then(data => {
        this.places = data;
      });
  }

  navigateToPlace(placeName: string) {
    this.router.navigate(['place/', placeName]);
  }

  navigateToResources() {
    this.router.navigate(['resourceOverview']);
  }

}
