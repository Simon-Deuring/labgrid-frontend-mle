import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
    selector: 'app-place-deletion-dialog',
    templateUrl: './place-deletion-dialog.component.html',
    styleUrls: ['./place-deletion-dialog.component.css'],
})
export class PlaceDeletionDialogComponent {
    constructor(
        public dialogRef: MatDialogRef<PlaceDeletionDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public placeName: string
    ) {}

    onCancelClick(): void {
        this.dialogRef.close();
    }
}
