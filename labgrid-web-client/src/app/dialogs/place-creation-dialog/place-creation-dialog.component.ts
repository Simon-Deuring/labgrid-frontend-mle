import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
    selector: 'app-place-creation-dialog',
    templateUrl: './place-creation-dialog.component.html',
    styleUrls: ['./place-creation-dialog.component.css'],
})
export class PlaceCreationDialogComponent {
    constructor(
        public dialogRef: MatDialogRef<PlaceCreationDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public placeName: string
    ) {}

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
