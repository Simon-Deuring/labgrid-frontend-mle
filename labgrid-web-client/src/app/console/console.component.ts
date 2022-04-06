import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Place } from 'src/models/place';
import { Resource } from 'src/models/resource';

import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';

@Component({
    selector: 'app-console',
    templateUrl: './console.component.html',
    styleUrls: ['./console.component.css'],
})
export class ConsoleComponent {
    place: Place = new Place('', [], '', false, [], '', null);
    private networkSerialPort: Resource = new Resource('', '', '', '', false, '', {});

    constructor(
        private _ps: PlaceService,
        private _rs: ResourceService,
        private route: ActivatedRoute,
        private router: Router
    ) {
        const placeName = this.route.snapshot.url[this.route.snapshot.url.length - 1].path;
        this._ps
            .getPlace(placeName)
            .then((data) => {
                if (data !== undefined) {
                    this.place = data;

                    let resourceName: string = '';
                    for (let i = 0; i < this.place.acquired_resources.length; i++) {
                        if (this.place.acquired_resources[i][2] === 'NetworkSerialPort') {
                            resourceName = this.place.acquired_resources[i][3];
                            return;
                        }
                    }

                    if (resourceName !== '') {
                        this._rs.getResourceByName(resourceName, placeName).then((resource) => {
                            if (resource !== undefined) {
                                this.networkSerialPort = resource;
                                this.setInitialText;
                            }
                        });
                    } else {
                        this.router.navigate(['error']);
                    }
                } else {
                    this.router.navigate(['error']);
                }
            })
            .catch(() => this.router.navigate(['error']));
    }

    private setInitialText(): void {
        const consoleElement = document.getElementById('console');
        if (consoleElement !== null) {
            consoleElement.innerText =
                "connecting to NetworkSerialPort(target=Target(name='" +
                this.place.name +
                "', env=Environment(config_file='/etc/labgrid/client.yaml')), name='" +
                this.networkSerialPort.name +
                "', state=<BindingState.bound: 1>, avail=" +
                (this.networkSerialPort.avail === true ? 'True' : 'False') +
                ", host='" +
                this.place.exporter +
                "', port=" +
                this.networkSerialPort.params.port +
                ', speed=' +
                this.networkSerialPort.params.speed +
                ", protocol='rfc2217') calling microcom -s " +
                this.networkSerialPort.params.speed +
                ' -t ' +
                this.networkSerialPort.target +
                ':' +
                this.networkSerialPort.target +
                '\nconnected to 127.0.0.1 (port ' +
                this.networkSerialPort.params.port +
                ')\nEscape character: Ctrl-\\\nType the escape character followed by c to get to the menu or q to quit';
        }
    }
}
