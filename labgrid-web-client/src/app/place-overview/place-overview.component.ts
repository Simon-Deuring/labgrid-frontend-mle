import { AfterViewInit, Component, OnInit, ViewChild, ViewContainerRef } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Place } from 'src/models/place';
import { PlaceService } from '../services/place.service';
import { ResourceService } from '../services/resource.service';

@Component({
  selector: 'app-place-overview',
  templateUrl: './place-overview.component.html',
  styleUrls: ['./place-overview.component.css']
})
export class PlaceOverviewComponent implements OnInit {
  
  places: Place[] = [];
  dataSource: MatTableDataSource<any> = new MatTableDataSource();
  displayedColumns: string[] = ['name', 'aquiredResources', 'aquired', 'isRunning'];
  
  @ViewChild('paginator') paginator!: MatPaginator;

  constructor(private placeService: PlaceService, private resourceService: ResourceService) {
    this.dataSource= new MatTableDataSource(this.places)
  }
  
  ngOnInit(): void {
    this.placeService.getPlaces()
      .then(data => {
        this.places = data;
        this.dataSource = new MatTableDataSource(this.places);
        this.dataSource.paginator = this.paginator;
      });
  }



  getAquiredName (aquired: string): string {
    return this.placeService.getAquiredName(aquired);
  }

  getResourceName(resource: string): string {
    return this.placeService.getResourceName(resource);
  }

  getRunningIcon (isRunning: boolean): string {
    if (isRunning) {
      return 'check_circle';
    } else {
      return 'cancel';
    }
  }
  
  
  applyFilter(event: Event) {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

}
