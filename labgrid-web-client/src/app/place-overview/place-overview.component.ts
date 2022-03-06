import { AfterViewInit, Component, OnInit, ViewChild, ViewContainerRef } from '@angular/core';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Router } from '@angular/router';
import { Place } from 'src/models/place';
import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';

@Component({
    selector: 'app-place-overview',
    templateUrl: './place-overview.component.html',
    styleUrls: ['./place-overview.component.css'],
})
export class PlaceOverviewComponent implements OnInit {
    places: Place[] = [];
    dataSource: MatTableDataSource<any> = new MatTableDataSource();
    displayedColumns: string[] = ['name', 'acquired_resources', 'acquired', 'isRunning'];

    @ViewChild('paginator') paginator!: MatPaginator;

    constructor(private _ps: PlaceService, private router: Router) {
        this.dataSource = new MatTableDataSource(this.places);
    }

    ngOnInit(): void {
        this._ps.getPlaces().then((data) => {
            this.places = data;
            this.dataSource = new MatTableDataSource(this.places);
            this.dataSource.paginator = this.paginator;
        });
    }

    getPowerStateIcon(isRunning: boolean): string {
        if (isRunning) {
            return 'power';
        } else {
            return 'power_off';
        }
    }

    applyFilter(event: Event) {
        const filterValue = (event.target as HTMLInputElement).value;
        this.dataSource.filter = filterValue.trim().toLowerCase();
    }

    navigateToPlace(placeName: string) {
        this.router.navigate(['place/', placeName]);
    }

    navigateToResource(resourceName: string, event: Event) {
        const correspondingPlace = (event.currentTarget as HTMLInputElement).parentNode?.parentNode?.firstChild
            ?.textContent;
        this.router.navigate(['resource/', resourceName, { placeName: correspondingPlace }]);
    }
}
