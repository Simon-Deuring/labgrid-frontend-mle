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
    styleUrls: ['./place.component.css'],
})
export class PlaceComponent implements OnInit {
    @ViewChild('placeStateTable') table!: MatTable<any>;

    place: Place = new Place('', [], '', false, [], '', AllocationState.Invalid);
    resources: Resource[] = [];
    placeStates: Array<{ name: string; value: string }> = [];
    displayedColumns: Array<string> = ['state-name', 'state-value'];
    allocationStateInvalid = false;
    isAcquired = false;
    isAcquiredByUser = false;

    constructor(
        private _ps: PlaceService,
        private _rs: ResourceService,
        private _snackBar: MatSnackBar,
        private route: ActivatedRoute,
        private router: Router
    ) {
        route.params.subscribe((val) => {
            const currentRoute = route.snapshot.url[route.snapshot.url.length - 1].path;
            this._ps.getPlace(currentRoute).then((data) => {
                // Check if the specified place exists
                if (Array.isArray(data) && data.length > 0) {
                    this.place = data[0];
                    this.getResources();
                    this.readPlaceState();
                    this.table.renderRows();
                } else {
                    this.router.navigate(['error']);
                }
            });
        });
    }

    ngOnInit(): void {}

    private getResources(): void {
        this._rs.getResourcesForPlace(this.place.name).then((resources) => {
            this.resources = resources;
        });
    }

    public navigateToResource(resourceName: string) {
        this.router.navigate(['resource/', resourceName, { placeName: this.place.name }]);
    }

    private readPlaceState(): void {
        this.placeStates = [];
        this.allocationStateInvalid = false;

        if (this.place.exporter) {
            this.placeStates.push({ name: 'Host name: ', value: this.place.exporter });
        }

        if (this.place.power_state) {
            this.placeStates.push({ name: 'Power State: ', value: 'on' });
        } else {
            this.placeStates.push({ name: 'Power State: ', value: 'off' });
        }

        /*const allocationEnum = (<any>AllocationState)[this.place.reservation];
        switch (allocationEnum) {
            case AllocationState.Allocated:
                this.placeStates.push({ name: 'Allocation status: ', value: this.place.reservation.toString() });
                break;
            case AllocationState.Acquired:
                this.placeStates.push({ name: 'Allocation status: ', value: this.place.reservation.toString() });
                break;
            case AllocationState.Expired:
                this.placeStates.push({ name: 'Allocation status: ', value: this.place.reservation.toString() });
                break;
            case AllocationState.Invalid:
                this.placeStates.push({ name: 'Allocation status: ', value: this.place.reservation.toString() });
                this.allocationStateInvalid = true;
                break;
            case AllocationState.Waiting:
                this.placeStates.push({ name: 'Allocation status: ', value: this.place.reservation.toString() });
                break;
            default:
                this.placeStates.push({
                    name: 'Allocation status: ',
                    value: 'something went wrong: ' + this.place.reservation.toString(),
                });
                break;
        }*/

        // TODO: Check if place was aquired by current user, if so set is isAquiredByUser to true for enabling the release button
        if (!this.place.acquired) {
            this.placeStates.push({ name: 'Acquired: ', value: 'no' });
            this.isAcquired = false;
        } else {
            this.placeStates.push({ name: 'Acquired: ', value: this.place.acquired });
            this.isAcquired = true;
        }
    }

    public async acquirePlace() {
        const ret = await this._ps.acquirePlace(this.route.snapshot.url[this.route.snapshot.url.length - 1].path);

        if (ret) {
            this._snackBar.open('Place has been acquired succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
        }
    }

    public async releasePlace() {
        const ret = await this._ps.releasePlace(this.route.snapshot.url[this.route.snapshot.url.length - 1].path);
        if (ret) {
            this._snackBar.open('Place has been released succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
        }
    }

    public async reservePlace() {
        const ret = await this._ps.reservePlace(this.route.snapshot.url[this.route.snapshot.url.length - 1].path);
        if (ret) {
            this._snackBar.open('Place has been reserved succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
        }
    }

    public async resetPlace() {
        // TODO: Call Reset RPC
        const response = false;

        if (response === false) {
            this._snackBar.open('During the reset an error has occured!', 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        } else {
            this._snackBar.open('Place has been reset succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
        }
    }
}
