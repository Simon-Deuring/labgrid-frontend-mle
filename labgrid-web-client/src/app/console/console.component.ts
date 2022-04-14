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
    allowInput: boolean = false;

    private session: any;
    private subscribe: boolean = true;
    private unsubscribe = (event: KeyboardEvent): void => {
        if (event.ctrlKey && event.key === 'c') {
            this.subscribe = false;

            if (this.consoleElement !== null) {
                this.completeText += "\n\nEnter command. Try 'help' for a list of builtin commands\n-> ";
                this.consoleElement.innerText = this.completeText;
                this.consoleElement.scrollTop = this.consoleElement.scrollHeight;
                this.allowInput = true;

                if (this.inputElement !== null) {
                    // This workaround is needed for focus() to work
                    window.setTimeout(() => {
                        this.inputElement?.focus();
                    }, 0);
                }
            }
        }
    };

    private consoleElement: HTMLElement | null = null;
    private inputElement: HTMLElement | null = null;
    private completeText: string = '';

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

                                this.setInitialText();
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
                session.subscribe('localhost.consoles.' + component.place.name, (args: string[]) => {
                    // Called when a new message is received
                    if (component.subscribe === true && component.consoleElement !== null) {
                        component.completeText += '\n' + args[0];
                        component.consoleElement.innerText = component.completeText;
                        component.consoleElement.scrollTop = component.consoleElement.scrollHeight;
                    }
                });
            } else {
                component.connectionError = true;
            }
        };

        connection.open();
    }

    private setInitialText(): void {
        this.consoleElement = document.getElementById('output-area');
        this.inputElement = document.getElementById('input-area');

        // If the user types ctrl + c the console stops displaying new messages
        document.addEventListener('keydown', this.unsubscribe);

        if (this.consoleElement !== null) {
            this.completeText =
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
                ')\nType Ctrl + c to get to the menu';

            this.consoleElement.innerText = this.completeText;
        }
    }

    // Called when the component is destroyed
    async ngOnDestroy(): Promise<void> {
        document.removeEventListener('keydown', this.unsubscribe);

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
