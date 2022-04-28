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
    public receivedAnswer: boolean = true;

    private lastCommand: string = '';

    private session: any;
    private subscribe: boolean = true;

    private toConsoleMenu = async (event: KeyboardEvent): Promise<void> => {
        // Called when a user types Ctrl + q
        if (this.subscribe === true && event.ctrlKey && event.key === 'q') {
            this.subscribe = false;

            if (this.consoleElement !== null && this.inputElement !== null) {
                this.completeText += "\n\nEnter command. Try 'help' for a list of builtin commands\n";
                this.consoleElement.innerText = this.completeText;
                this.inputElement.scrollIntoView(false);
                this.allowInput = true;

                // This workaround is needed for focus() to work
                window.setTimeout(() => {
                    this.inputElement?.focus();
                }, 0);
            }
        }
        // Called when the user types Enter
        else if (event.key === 'Enter') {
            event.preventDefault();
            this.subscribe = false;

            if (this.consoleElement != null && this.inputElement !== null) {
                let userCommand = this.inputElement.textContent;

                if (userCommand !== null) {
                    this.inputElement.textContent = '';

                    this.completeText += '-> ' + userCommand + '\n';
                    this.consoleElement.innerText = this.completeText;
                    this.inputElement.scrollIntoView(false);
                    this.receivedAnswer = false;

                    // If the user types 'exit' the command can directly be processed
                    if (userCommand === '') {
                        this.allowInput = true;
                        this.receivedAnswer = true;

                        this.consoleElement.innerText = this.completeText;
                        this.inputElement.scrollIntoView(false);
                        return;
                    }
                    if (userCommand === 'exit') {
                        this.allowInput = false;

                        this.completeText += '\n----------------------\n';
                        this.consoleElement.innerText = this.completeText;
                        this.inputElement.scrollIntoView(false);
                    }
                    // All other commands are sent to the backend
                    else {
                        this.lastCommand = '-> ' + userCommand;

                        await this.session.call('localhost.console_write', [this.place.name, '\x1c\n']);
                        this.session.call('localhost.console_write', [this.place.name, userCommand]);

                        // Listen for the response
                        this.subscribe = true;
                    }
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
                        if (
                            args[0] !== component.lastCommand &&
                            !args[0].startsWith('connected to 127.0.1.1') &&
                            args[0] !== 'Escape character: Ctrl-\\' &&
                            args[0] !== 'Type the escape character followed by c to get to the menu or q to quit' &&
                            args[0] !== '' &&
                            args[0] !== '->' &&
                            args[0] !== "Enter command. Try 'help' for a list of builtin commands"
                        ) {
                            component.completeText += args[0] + '\n';
                            component.consoleElement.innerText = component.completeText;
                            component.receivedAnswer = true;

                            if (component.inputElement !== null) {
                                component.inputElement.scrollIntoView(false);
                                window.setTimeout(() => {
                                    component.inputElement?.focus();
                                }, 0);
                            }
                        }
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

        // If the user types ctrl + q the console stops displaying new messages
        document.addEventListener('keydown', this.toConsoleMenu);

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
                ')\nType Ctrl + q to get to the menu';

            this.consoleElement.innerText = this.completeText;
        }
    }

    // Called when the component is destroyed
    async ngOnDestroy(): Promise<void> {
        document.removeEventListener('keydown', this.toConsoleMenu);

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
