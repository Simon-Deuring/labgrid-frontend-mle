import { Component, OnInit } from '@angular/core';
import { PlaceService } from '../place.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent implements OnInit {

  public places: any = [];

  constructor(private _ps: PlaceService) { }

  ngOnInit(): void {
    this._ps.getPlaces()
      .then(data => {
        this.places = data;
      });
  }
}
