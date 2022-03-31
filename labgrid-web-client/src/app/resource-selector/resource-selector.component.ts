import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Place } from 'src/models/place';
import { Resource } from 'src/models/resource';
import { AllocationState } from '../_enums/allocation-state';
import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';
import {CdkDragDrop, moveItemInArray, transferArrayItem} from '@angular/cdk/drag-drop';

@Component({
  selector: 'app-resource-selector',
  templateUrl: './resource-selector.component.html',
  styleUrls: ['./resource-selector.component.css']
})
export class ResourceSelectorComponent implements OnInit {

  place: Place = new Place('', [], '', false, [], '', AllocationState.Invalid);
  resources: Resource[] = [];

  assignedResources: string[] = [];
  availableResources: string[] = [];


  constructor(
    private _ps: PlaceService,
    private _rs: ResourceService, 
    private route: ActivatedRoute, 
    private router: Router) {
      this.getPlaceData()
     }

  ngOnInit(): void {
  }

  private getResources(): void {
    this._rs.getResourcesForPlace(this.place.name).then((resources) => {
      this.resources = resources;
      // this.assignedResources = resources;
      resources.forEach(x => {
        this.assignedResources.push(x.name);
        this.availableResources.push(x.name);
      })
    });
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
          this.router.navigate(['error']);
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
}
