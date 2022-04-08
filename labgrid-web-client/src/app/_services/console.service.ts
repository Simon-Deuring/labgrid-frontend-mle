import { Injectable } from '@angular/core';
import * as autobahn from 'autobahn-browser';

@Injectable({
    providedIn: 'root',
})
export class ConsoleService {
    private session: any;

    constructor() {
        const connection = new autobahn.Connection({
            url: 'ws://localhost:8083/ws',
            realm: 'frontend',
        });

        let service = this;
        connection.onopen = async function (session: any, details: any) {
            service.session = session;
        };

        connection.open();
    }

    public async openConsole(placeName: string): Promise<boolean> {
        if (this.session) {
            const result = await this.session.call('localhost.console', [placeName]);
            return result;
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });

            const result = await this.session.call('localhost.console', [placeName]);
            return result;
        }
    }
}
