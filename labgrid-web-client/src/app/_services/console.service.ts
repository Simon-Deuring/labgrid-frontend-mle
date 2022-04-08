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
        const result = await this.session.call('localhost.console', [placeName]);
        return result;
    }
}
