import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { PlaceService } from '../_services/place.service';
import { MatDialog } from '@angular/material/dialog';
import { PlaceCreationDialogComponent } from '../dialogs/place-creation-dialog/place-creation-dialog.component';

@Component({
    selector: 'app-sidebar',
    templateUrl: './sidebar.component.html',
    styleUrls: ['./sidebar.component.css'],
})
export class SidebarComponent implements OnInit {
    public places: any = [];

    constructor(private _ps: PlaceService, private router: Router, private dialog: MatDialog) {}

    ngOnInit(): void {
        this._ps.getPlaces().then((data) => {
            this.places = data;
        });
    }

    navigateToPlace(placeName: string) {
        this.router.navigate(['place/', placeName]);
    }

    navigateToResources() {
        this.router.navigate(['resourceOverview']);
    }

    navigateToOverview() {
        this.router.navigate(['/']);
    }

    getAvailableIcon(isAvailable: boolean): string {
        if (isAvailable) {
            return 'lock';
        } else {
            return 'lock_open';
        }
    }

    openNewPlaceDialog(): void {
        const dialogRef = this.dialog.open(PlaceCreationDialogComponent);

        dialogRef.afterClosed().subscribe((result) => {
            this._ps.createNewPlace(result);
        });
    }
}
