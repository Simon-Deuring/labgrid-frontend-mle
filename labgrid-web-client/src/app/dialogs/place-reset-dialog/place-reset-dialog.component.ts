import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
    selector: 'app-place-reset-dialog',
    templateUrl: './place-reset-dialog.component.html',
    styleUrls: ['./place-reset-dialog.component.css'],
})
export class PlaceResetDialogComponent {
    constructor(
        public dialogRef: MatDialogRef<PlaceResetDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public placeName: string
    ) {}

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
