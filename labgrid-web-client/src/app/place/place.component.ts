import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { PlaceService } from '../_services/place.service';
import { Place } from '../../models/place';
import { ResourceService } from '../_services/resource.service';
import { Resource } from '../../models/resource';
import { AllocationState } from '../_enums/allocation-state';
import { MatTable, MatTableDataSource } from '@angular/material/table';

@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.css']
})
export class PlaceComponent implements OnInit {

  @ViewChild('placeStateTable') table!: MatTable<any>;
  
  place: Place = new Place('', false, '','', "Invalid", []);
  resources: Resource[] = [];

  placeStates: Array<{name: string, value: string}> = [];
  displayedColumns: Array<string> = ['state-name', 'state-value'];

  dataReady: boolean = false;

  constructor(private _ps: PlaceService, private _rs: ResourceService, private route: ActivatedRoute, private router: Router) {
    route.params.subscribe(val => {
      const currentRoute = route.snapshot.url[route.snapshot.url.length-1].path;
      this._ps.getPlace(currentRoute).then(data => {
        this.place = data;
        this.getResources();

        this.readPlaceState();
        this.table.renderRows();
      });
    })
  }

  ngOnInit(): void {
    // this.readPlaceState();
  }

  private getResources(): void {
    this._rs.getResourcesForPlace(this.place.name).then(resources => {
      this.resources = resources;
    });
  }

  public navigateToResource(resourceName: string) {
    this.router.navigate(['resource/', resourceName]);
  }

  private readPlaceState(): void {

    this.placeStates = [];

    if (this.place.matches) {
      this.placeStates.push({name: 'Matches: ', value: this.place.matches});
    }
    if (this.place.isRunning) {
      this.placeStates.push({name: 'Is running: ', value: 'yes'});
    } else {
      this.placeStates.push({name: 'Is running: ', value: 'no'});
    }
    if (!this.place.aquired) {
      this.placeStates.push({name: 'Aquired: ', value: 'no'});
    } else {
      this.placeStates.push({name: 'Aquired: ', value: this.place.aquired});
    }

    const allocationEnum = (<any>AllocationState)[this.place.allocation];
    switch (allocationEnum){
      case AllocationState.Allocated: 
        this.placeStates.push({name: 'allocation state: ', value: this.place.allocation});
        break;
      case AllocationState.Aquired: 
        this.placeStates.push({name: 'allocation state: ', value: this.place.allocation});
        break;
      case AllocationState.Expired: 
        this.placeStates.push({name: 'allocation state: ', value: this.place.allocation});
        break;
      case AllocationState.Invalid:
        this.placeStates.push({name: 'allocation state: ', value: this.place.allocation});
        break;
      case AllocationState.Waiting:
        this.placeStates.push({name: 'allocation state: ', value: this.place.allocation});
        break;
      default:
        this.placeStates.push({name: 'allocation state: ', value: 'something went wrong: ' + this.place.allocation});
        break;
    }
    this.dataReady = true;
  }

}
