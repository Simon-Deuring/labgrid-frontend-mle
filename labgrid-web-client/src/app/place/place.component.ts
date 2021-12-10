import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { PlaceService } from '../_services/place.service';
import { Place } from '../../models/place';
import { ResourceService } from '../_services/resource.service';
import { Resource } from '../../models/resource';
import { AllocationState } from '../_enums/allocation-state';
import { MatTable } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.css']
})
export class PlaceComponent implements OnInit {

  @ViewChild('placeStateTable') table!: MatTable<any>;

  place: Place = new Place('', false, '', '', "Invalid", []);
  resources: Resource[] = [];
  placeStates: Array<{ name: string, value: string }> = [];
  displayedColumns: Array<string> = ['state-name', 'state-value'];
  allocationStateInvalid = false;
  isAquired = false;

  constructor(private _ps: PlaceService, private _rs: ResourceService, private _snackBar: MatSnackBar, private route: ActivatedRoute, private router: Router) {
    route.params.subscribe(val => {
      const currentRoute = route.snapshot.url[route.snapshot.url.length - 1].path;
      this._ps.getPlace(currentRoute).then(data => {
        this.place = data;
        this.getResources();
        this.readPlaceState();
        this.table.renderRows();
      });
    })
  }

  ngOnInit(): void { }

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
    this.allocationStateInvalid = false;

    if (this.place.matches) {
      this.placeStates.push({ name: 'Host name: ', value: this.place.matches.split('/')[0] });
    }
    if (this.place.isRunning) {
      this.placeStates.push({ name: 'Is running: ', value: 'yes' });
    } else {
      this.placeStates.push({ name: 'Is running: ', value: 'no' });
    }

    const allocationEnum = (<any>AllocationState)[this.place.allocation];
    switch (allocationEnum) {
      case AllocationState.Allocated:
        this.placeStates.push({ name: 'Allocation status: ', value: this.place.allocation });
        break;
      case AllocationState.Aquired:
        this.placeStates.push({ name: 'Allocation status: ', value: this.place.allocation });
        break;
      case AllocationState.Expired:
        this.placeStates.push({ name: 'Allocation status: ', value: this.place.allocation });
        break;
      case AllocationState.Invalid:
        this.placeStates.push({ name: 'Allocation status: ', value: this.place.allocation });
        this.allocationStateInvalid = true;
        break;
      case AllocationState.Waiting:
        this.placeStates.push({ name: 'Allocation status: ', value: this.place.allocation });
        break;
      default:
        this.placeStates.push({ name: 'Allocation status: ', value: 'something went wrong: ' + this.place.allocation });
        break;
    }

    if (!this.place.aquired) {
      this.placeStates.push({ name: 'Aquired: ', value: 'no' });
      this.isAquired = false;
    } else {
      this.placeStates.push({ name: 'Aquired: ', value: this.place.aquired });
      this.isAquired = true;
    }
  }

  public async aquirePlace() {
    const ret = await this._ps.aquirePlace(this.route.snapshot.url[this.route.snapshot.url.length - 1].path);

    if (ret) {
      this._snackBar.open('Place was aquired succesfully!', 'OK',
        {
          duration: 3000,
          panelClass: ['success-snackbar']
        });
    }
  }

}
