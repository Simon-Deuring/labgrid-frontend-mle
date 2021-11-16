import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { PlaceService } from '../place.service';
import { Place } from '../../models/place';

@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.css']
})
export class PlaceComponent implements OnInit {

  place = new Place('','','','');
  currentRoute = '';

  constructor(private placeService: PlaceService, private route: ActivatedRoute, router: Router) {
    route.params.subscribe(val => {
      this.currentRoute = route.snapshot.url[route.snapshot.url.length-1].path;
      this.placeService.getPlace(this.currentRoute).then(data => {
        this.place = data;
      });
    })

  }

  ngOnInit(): void {

    
  }

}
