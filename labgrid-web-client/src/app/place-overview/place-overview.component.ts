import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';

import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatTableDataSource } from '@angular/material/table';

import { Place } from 'src/models/place';
import { PlaceCreationDialogComponent } from '../dialogs/place-creation-dialog/place-creation-dialog.component';
import { PlaceDeletionDialogComponent } from '../dialogs/place-deletion-dialog/place-deletion-dialog.component';
import { PlaceService } from '../_services/place.service';

@Component({
    selector: 'app-place-overview',
    templateUrl: './place-overview.component.html',
    styleUrls: ['./place-overview.component.css'],
})
export class PlaceOverviewComponent implements OnInit {
    places: Place[] = [];
    dataSource: MatTableDataSource<any> = new MatTableDataSource();
    displayedColumns: string[] = ['name', 'acquired_resources', 'acquired', 'isPowerStateOn', 'actions'];
    loading = true;

    @ViewChild('paginator') paginator!: MatPaginator;

    constructor(
        private _dialog: MatDialog,
        private _ps: PlaceService,
        private _router: Router,
        private _snackBar: MatSnackBar
    ) {
        this.dataSource = new MatTableDataSource(this.places);
    }

    ngOnInit(): void {
        this.loadPlaces();
        this._ps.places.subscribe((newState) => {
            this.places = newState;
            this.dataSource = new MatTableDataSource(this.places);
            this.dataSource.paginator = this.paginator;
        });
    }

    private loadPlaces(): void {
        this._ps
            .getPlaces()
            .then((data) => {
                this.places = data;
                this.dataSource = new MatTableDataSource(this.places);
                this.dataSource.paginator = this.paginator;
            })
            .then(() => (this.loading = false));
    }

    getPowerStateIcon(isPowerStateOn: boolean): string {
        if (isPowerStateOn) {
            return 'power';
        } else {
            return 'power_off';
        }
    }

    applyFilter(event: Event) {
        const filterValue = (event.target as HTMLInputElement).value;
        this.dataSource.filter = filterValue.trim().toLowerCase();
    }

    navigateToPlace(placeName: string) {
        this._router.navigate(['place/', placeName]);
    }

    navigateToResource(resourceName: string, event: Event) {
        const correspondingPlace = (event.currentTarget as HTMLInputElement).parentNode?.parentNode?.firstChild
            ?.textContent;
        this._router.navigate(['resource/', resourceName, { placeName: correspondingPlace }]);
    }

    openNewPlaceDialog(): void {
        const dialogRef = this._dialog.open(PlaceCreationDialogComponent);

        dialogRef.afterClosed().subscribe((result) => {
            if (result !== undefined) this.createNewPlace(result);
        });
    }

    openDeletePlaceDialog(placeName: string): void {
        const dialogRef = this._dialog.open(PlaceDeletionDialogComponent, {
            data: placeName,
            autoFocus: false,
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result !== undefined) this.deletePlace(placeName);
        });
    }

    private async createNewPlace(placeName: string) {
        const response = await this._ps.createNewPlace(placeName);

        if (response.successful) {
            this._snackBar.open('Place has been added succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
            this.loadPlaces();
        } else {
            this._snackBar.open(response.errorMessage, 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        }
    }

    private async deletePlace(placeName: string) {
        const response = await this._ps.deletePlace(placeName);

        if (response.successful) {
            this._snackBar.open('Place has been deleted succesfully!', 'OK', {
                duration: 3000,
                panelClass: ['success-snackbar'],
            });
            this.loadPlaces();
        } else {
            this._snackBar.open(response.errorMessage, 'OK', {
                duration: 3000,
                panelClass: ['error-snackbar'],
            });
        }
    }
}
