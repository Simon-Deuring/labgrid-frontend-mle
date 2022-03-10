import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

import { PlaceCreationDialogComponent } from '../dialogs/place-creation-dialog/place-creation-dialog.component';
import { PlaceService } from '../_services/place.service';

@Component({
    selector: 'app-sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.css'],
})
export class SidebarComponent implements OnInit {
    public places: any = [];

    constructor(
        private _dialog: MatDialog,
        private _ps: PlaceService,
        private _router: Router,
        private _snackBar: MatSnackBar
    ) {}

    ngOnInit(): void {
        this.loadPlaces();
        this._ps.places.subscribe((newState) => (this.places = newState));
    }

    private loadPlaces(): void {
        this._ps.getPlaces().then((data) => {
            this.places = data;
        });
    }

    navigateToPlace(placeName: string) {
        this._router.navigate(['place/', placeName]);
    }

    navigateToResources() {
        this._router.navigate(['resourceOverview']);
    }

    navigateToOverview() {
        this._router.navigate(['/']);
    }

    getAvailableIcon(isAvailable: boolean): string {
        if (isAvailable) {
            return 'lock';
        } else {
            return 'lock_open';
        }
    }

    openNewPlaceDialog(): void {
        const dialogRef = this._dialog.open(PlaceCreationDialogComponent);

        dialogRef.afterClosed().subscribe((result) => {
            if (result) this.createNewPlace(result);
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
}
