import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Place } from 'src/models/place';
import { Resource } from 'src/models/resource';
import { AllocationState } from '../_enums/allocation-state';
import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';
import { CdkDragDrop, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';
import { MatDialog } from '@angular/material/dialog';
import { CancelDialogComponent } from '../dialogs/cancel-dialog/cancel-dialog.component';

@Component({
  selector: 'app-resource-selector',
  templateUrl: './resource-selector.component.html',
  styleUrls: ['./resource-selector.component.css']
})
export class ResourceSelectorComponent implements OnInit {

  place: Place = new Place('', [], '', false, [], '', null);
  loading = true;
  resources: Resource[] = [];

  assignedResources: string[] = [];
  availableResources: string[] = [];


  constructor(
    private _ps: PlaceService,
    private _rs: ResourceService,
    private route: ActivatedRoute,
    private _router: Router,
    private _dialog: MatDialog) {
    this.getPlaceData()
  }

  ngOnInit(): void {
  }

  private getResources(): void {
    this._rs.getResourcesForPlace(this.place.name).then((resources) => {
      this.resources = resources;
      // this.assignedResources = resources;
      resources.forEach(x => {
        if (x.acquired) {
          this.assignedResources.push(x.name);
        } else {
          this.availableResources.push(x.name);
        }
      })
    }).then(()=> this.loading = false);

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
        if (Array.isArray(data) && data.length > 0) {
          this.place = data[0];
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
        event.currentIndex,
      );
    }
  }

  saveResources() {
    const removedResources: string[] = []
    const addedResources: string[] = []

    // get deleted ressources
    this.resources.forEach(x => {
      if (!this.assignedResources.includes(x.name)) {
        console.log('this ressource is not in the assigned List. It has to be removed.');
        removedResources.push(x.name);
      }
    })

    // get added ressources
    this.assignedResources.forEach(x => {
      if (!this.resources.find(y => y.name === x)) {
        console.log('this ressource was added');
        addedResources.push(x);
      }
      /*if (this.resources.includes(x)) {
        console.log('this ressource is not in the assigned List. It has to be removed.');
        addedRessources.push(x);
      }*/
    })

    console.log('--------results--------')
    console.log('removed: ', removedResources)
    console.log('added: ', addedResources)

    this._rs.
  }

cancel() {
  const dialogRef = this._dialog.open(CancelDialogComponent, {
    autoFocus: false,
  });

  dialogRef.afterClosed().subscribe((result) => {
    console.log('dialog result: ', result)
    if (result !== undefined) {

      this._router.navigate(['place/', this.place.name]
      )
    };
  });

}
}
