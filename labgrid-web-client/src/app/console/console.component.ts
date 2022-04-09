import { Component, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import * as autobahn from 'autobahn-browser';

import { Place } from 'src/models/place';
import { Resource } from 'src/models/resource';

import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';

@Component({
    selector: 'app-console',
    templateUrl: './console.component.html',
    styleUrls: ['./console.component.css'],
})
export class ConsoleComponent implements OnDestroy {
    place: Place = new Place('', [], '', false, [], '', null);
    private networkSerialPort: Resource = new Resource('', '', '', '', false, '', {});

    connectionError: boolean = false;
    private session: any;

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
        const connection = new autobahn.Connection({
            url: 'ws://localhost:8083/ws',
            realm: 'frontend',
        });
        let component = this;

        connection.onopen = async function (session: any, details: any) {
            // Save the session to close it afterwards
            component.session = session;

            if (!session) {
                await new Promise((resolve, reject) => {
                    // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                    setTimeout(resolve, 1000);
                });
            }
            // Connect to the serial console and subscribe to events
            const result = await session.call('localhost.console', [component.place.name]);
            if (result === true) {
                session.subscribe('localhost.consoles.' + component.place.name, component.onMessageReceived);
            }
        };
        connection.open();

        this.setInitialText();
    }

    private onMessageReceived(args: string[]) {
        console.log(args[0]);
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

    // Called when the component is destroyed
    async ngOnDestroy(): Promise<void> {
        if (
            this.session != undefined &&
            this.place != undefined &&
            this.place.name !== undefined &&
            this.place.name !== ''
        ) {
            await this.session.call('localhost.console_close', [this.place.name]);
        }
    }
}
