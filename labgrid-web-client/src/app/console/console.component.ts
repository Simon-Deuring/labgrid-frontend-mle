import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Place } from 'src/models/place';
import { Resource } from 'src/models/resource';

import { ConsoleService } from '../_services/console.service';
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

    connectionError: boolean = false;

    constructor(
        private _cs: ConsoleService,
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
                    this.place.acquired_resources.forEach((resource) => {
                        if (resource[2] === 'NetworkSerialPort') {
                            resourceName = resource[3];
                            return;
                        }
                    });

                    if (resourceName !== '') {
                        this._rs.getResourceByName(resourceName, placeName).then((resource) => {
                            if (resource !== undefined) {
                                this.networkSerialPort = resource;
                                this.openConsole();
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

    private async openConsole(): Promise<void> {
        // Connect to the serial console
        let connectionStatus = await this._cs.openConsole(this.place.name);

        if (connectionStatus === true) {
            // Set the initial text in the console
            this.setInitialText();
        } else {
            this.connectionError = true;
        }
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
                this.networkSerialPort.params.host +
                "', port=" +
                this.networkSerialPort.params.port +
                ', speed=' +
                this.networkSerialPort.params.speed +
                ", protocol='rfc2217') calling microcom -s " +
                this.networkSerialPort.params.speed +
                ' -t ' +
                this.networkSerialPort.params.host +
                ':' +
                this.networkSerialPort.params.port +
                '\nconnected to 127.0.0.1 (port ' +
                this.networkSerialPort.params.port +
                ')\nEscape character: Ctrl-\\\nType the escape character followed by c to get to the menu or q to quit\n';
        }
    }
}
