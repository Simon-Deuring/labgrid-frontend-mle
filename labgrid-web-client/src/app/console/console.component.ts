import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Place } from 'src/models/place';
import { PlaceService } from '../_services/place.service';

@Component({
    selector: 'app-console',
    templateUrl: './console.component.html',
    styleUrls: ['./console.component.css'],
})
export class ConsoleComponent {
    private place: Place = new Place('', [], '', false, [], '', null);

    constructor(private _ps: PlaceService, private route: ActivatedRoute, private router: Router) {
        const placeName = this.route.snapshot.url[this.route.snapshot.url.length - 1].path;
        this._ps.getPlace(placeName).then((data) => {
            if (data !== undefined) {
                this.place = data;
            } else {
                this.router.navigate(['error']);
            }
        });
    }
}
