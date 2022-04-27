import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
    selector: 'app-cancel-dialog',
    templateUrl: './cancel-dialog.component.html',
    styleUrls: ['./cancel-dialog.component.css'],
})
export class CancelDialogComponent {
    constructor(public dialogRef: MatDialogRef<CancelDialogComponent>) {}

    onRevokeCancelClick(): void {
        this.dialogRef.close();
    }
}
