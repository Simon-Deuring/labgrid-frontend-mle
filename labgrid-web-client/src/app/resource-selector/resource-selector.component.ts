import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';

import { Place } from 'src/models/place';
import { Resource } from 'src/models/resource';

import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';

import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

import { CancelDialogComponent } from '../dialogs/cancel-dialog/cancel-dialog.component';

@Component({
    selector: 'app-resource-selector',
    templateUrl: './resource-selector.component.html',
    styleUrls: ['./resource-selector.component.css'],
})
export class ResourceSelectorComponent {
    place: Place = new Place('', [], '', false, [], '', null);
    resources: Resource[] = [];
    loading = true;

    assignedResources: string[] = [];
    availableResources: string[] = [];

    constructor(
        private _ps: PlaceService,
        private _rs: ResourceService,
        private route: ActivatedRoute,
        private _router: Router,
        private _snackBar: MatSnackBar,
        private _dialog: MatDialog
    ) {
        this.getPlaceData();
    }

    private getResources(): void {
        this._rs
            .getResourcesForPlace(this.place.name)
            .then((resources) => {
                this.resources = resources;
                // this.assignedResources = resources;
                resources.forEach((x) => {
                    if (x.acquired) {
                        this.assignedResources.push(x.name);
                    } else {
                        this.availableResources.push(x.name);
                    }
                });
            })
            .then(() => (this.loading = false));

        /*this._rs.getResourcesForPlace(this.place.name).then((resources) => {
      this.resources = resources;
      // this.assignedResources = resources;
      resources.forEach(x => {
        this.assignedResources.push(x.name);
      })
    });

    this._rs.getResources().then((resources) => {
      resources.forEach(x => {
        if (x.acquired === null) {
          this.availableResources.push(x.name);
          console.log('Resource: ', x)
        }
      })
    }).then(()=> this.loading = false);*/
    }

    private getPlaceData() {
        this.route.params.subscribe((val) => {
            const currentRoute = this.route.snapshot.url[this.route.snapshot.url.length - 1].path;
            this._ps.getPlace(currentRoute).then((data) => {
                // Check if the specified place exists
                if (data !== undefined) {
                    this.place = data;
                    this.getResources();
                } else {
                    this._router.navigate(['error']);
                }
            });
        });
    }

    drop(event: CdkDragDrop<string[]>) {
        if (event.previousContainer === event.container) {
            moveItemInArray(event.container.data, event.previousIndex, event.currentIndex);
        } else {
            transferArrayItem(
                event.previousContainer.data,
                event.container.data,
                event.previousIndex,
                event.currentIndex
            );
        }
    }

    saveResources() {
        const removedResources: string[] = [];
        const addedResources: string[] = [];

        // get deleted resources
        this.resources.forEach((x) => {
            if (!this.assignedResources.includes(x.name)) {
                // this resource is not in the assigned List. It has to be removed.
                removedResources.push(x.name);
            }
        });

        // get added resources
        this.assignedResources.forEach((x) => {
            if (!this.resources.find((y) => y.name === x)) {
                // this resource was added
                addedResources.push(x);
            }
        });

        // console.log('--------results--------')
        // console.log('removed: ', removedResources)
        // console.log('added: ', addedResources)

        let response = { successful: false, errorMessage: '' };
        removedResources.forEach(async (r) => {
            response = await this._rs.releaseResource(r, this.place.name);
            if (response.successful) {
                this._snackBar.open('Resources were released successfully.', 'OK', {
                    duration: 3000,
                    panelClass: ['success-snackbar'],
                });
            } else {
                this._snackBar.open(response.errorMessage, 'OK', {
                    duration: 3000,
                    panelClass: ['error-snackbar'],
                });
            }
        });

        addedResources.forEach(async (r) => {
            response = await this._rs.acquireResource(r, this.place.name);
            if (response.successful) {
                this._snackBar.open('Resources were acquired successfully.', 'OK', {
                    duration: 3000,
                    panelClass: ['success-snackbar'],
                });
            } else {
                this._snackBar.open(response.errorMessage, 'OK', {
                    duration: 3000,
                    panelClass: ['error-snackbar'],
                });
            }
        });

        this._router.navigate(['place/', this.place.name]);
    }

    cancel() {
        const dialogRef = this._dialog.open(CancelDialogComponent, {
            autoFocus: false,
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result !== undefined) {
                this._router.navigate(['place/', this.place.name]);
            }
        });
    }
}
