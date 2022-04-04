import { Component, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Place } from '../../models/place';
import { Resource } from '../../models/resource';

import { PlaceDeletionDialogComponent } from '../dialogs/place-deletion-dialog/place-deletion-dialog.component';
import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';

import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTable } from '@angular/material/table';

@Component({
    selector: 'app-place',
    templateUrl: './place.component.html',
    styleUrls: ['./place.component.css'],
})
export class PlaceComponent {
    @ViewChild('placeStateTable') table!: MatTable<any>;

    place: Place = new Place('', [], '', false, [], '', null);
    resources: Resource[] = [];

    placeStates: Array<{ name: string; value: string }> = [];
    displayedColumns: Array<string> = ['state-name', 'state-value'];

    isAcquired: boolean = false;
    isAcquiredByUser: boolean = false;

    hasNetworkSerialPort: boolean = false;

    constructor(
        private _dialog: MatDialog,
        private _ps: PlaceService,
        private _rs: ResourceService,
        private _snackBar: MatSnackBar,
        private route: ActivatedRoute,
        private router: Router
    ) {
        route.params.subscribe((val) => {
            this.updateData();
        });
    }

    private updateData() {
        this.route.params.subscribe((val) => {
            this.hasNetworkSerialPort = false;

            const currentRoute = this.route.snapshot.url[this.route.snapshot.url.length - 1].path;
            this._ps.getPlace(currentRoute).then((data: Place) => {
                // Check if the specified place exists
                if (data !== undefined) {
                    this.place = data;
                    this.getResources();
                    this.readPlaceState();
                    this.table.renderRows();

                    if (this.place.reservation !== undefined && this.place.reservation !== null) {
                        this.loadReservation(this.place.reservation);
                    }

                    this.checkForNetworkSerialConsole();
                } else {
                    this.router.navigate(['error']);
                }
            });
        });
    }

    private getResources(): void {
        this._rs.getResourcesForPlace(this.place.name).then((resources) => {
            this.resources = resources;
        });
    }

    private readPlaceState(): void {
        this.placeStates = [];

        if (this.place.exporter) {
            this.placeStates.push({ name: 'Host name: ', value: this.place.exporter });
        }

        if (this.place.power_state) {
            this.placeStates.push({ name: 'Power state: ', value: 'on' });
        } else {
            this.placeStates.push({ name: 'Power state: ', value: 'off' });
        }

        // TODO: user has to be replaced by dynamic username
        if (this.place.acquired === 'labby/dummy') {
            this.isAcquiredByUser = true;
        } else {
            this.isAcquiredByUser = false;
        }
        if (!this.place.acquired) {
            this.placeStates.push({ name: 'Acquired: ', value: 'no' });
            this.isAcquired = false;
        } else {
            this.placeStates.push({ name: 'Acquired: ', value: this.place.acquired });
            this.isAcquired = true;
        }
    }

    private async loadReservation(rName: string): Promise<void> {
        let reservations: any = await this._ps.getReservations();

        if (reservations[rName] !== undefined) {
            this.placeStates.push({ name: 'Status of reservation: ', value: reservations[rName].state });
            this.placeStates.push({ name: 'Reservation owner: ', value: reservations[rName].owner });
            this.placeStates.push({
                name: 'Reservation timeout: ',
                value: new Date(reservations[rName].timeout * 1000).toLocaleString('en-US'),
            });
            this.table.renderRows();
        }
    }

    private checkForNetworkSerialConsole(): void {
        for (let i = 0; i < this.place.acquired_resources.length; i++) {
            if (this.place.acquired_resources[i][2] === 'NetworkSerialPort') {
                this.hasNetworkSerialPort = true;
                return;
            }
        }

        // If no NetworkSerialPort has been found for the place
        this.hasNetworkSerialPort = false;
    }

    public navigateToResource(resourceName: string) {
        this.router.navigate(['resource/', resourceName, { placeName: this.place.name }]);
    }

    public async acquirePlace() {
        const ret = await this._ps.acquirePlace(this.route.snapshot.url[this.route.snapshot.url.length - 1].path);

        if (ret.successful) {
            this._snackBar.open('Place has been acquired succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
            this.updateData();
        } else if (!ret.successful && !ret.errorMessage) {
            this._snackBar.open('Place could not be acuired.', 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        } else {
            this._snackBar.open(ret.errorMessage, 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        }
    }

    public async releasePlace() {
        const ret = await this._ps.releasePlace(this.route.snapshot.url[this.route.snapshot.url.length - 1].path);
        if (ret.successful) {
            this._snackBar.open('Place has been released succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
            this.updateData();
        } else {
            this._snackBar.open(ret.errorMessage, 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        }
    }

    public async reservePlace() {
        const ret: any = await this._ps.reservePlace(this.route.snapshot.url[this.route.snapshot.url.length - 1].path);
        if (ret.error !== undefined && ret.error.message !== undefined) {
            this._snackBar.open(ret.error.message, 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        } else {
            this._snackBar.open('Place has been reserved succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
        }

        // Reload place to get reservation information
        const currentRoute = this.route.snapshot.url[this.route.snapshot.url.length - 1].path;
        this._ps.getPlace(currentRoute).then((data: Place) => {
            // Check if the specified place exists
            if (data !== undefined) {
                this.place = data;
                this.readPlaceState();
                this.table.renderRows();

                if (this.place.reservation !== undefined && this.place.reservation !== null) {
                    this.loadReservation(this.place.reservation);
                }
            } else {
                this.router.navigate(['error']);
            }
        });
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

    openDeletePlaceDialog(): void {
        const dialogRef = this._dialog.open(PlaceDeletionDialogComponent, {
            data: this.place.name,
            autoFocus: false,
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result !== undefined) this.deletePlace(result);
        });
    }

    private async deletePlace(placeName: string) {
        const response = await this._ps.deletePlace(placeName);

        if (response.successful) {
            this._snackBar.open('Place has been deleted succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
            this.router.navigate(['/']);
        } else {
            this._snackBar.open(response.errorMessage, 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        }
    }

    public startSerialConsole(): void {
        //
    }
}
