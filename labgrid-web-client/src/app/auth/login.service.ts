import { Injectable } from '@angular/core';

import * as autobahn from 'autobahn-browser';

@Injectable({
    providedIn: 'root',
})
export class LoginService {
    private session: any;

    public isLoggedIn: boolean = true; // Set to false in production mode
    public username: string = '';

    // Store the URL to redirect after logging in
    redirectUrl: string | null = null;

    constructor() {
        const connection = new autobahn.Connection({
            url: 'ws://localhost:8083/ws',
            realm: 'frontend',
        });

        let service = this;
        connection.onopen = async function (session: any, details: any) {
            service.session = session;
            service.readUsername(session, service);
        };

        connection.open();
    }

    private async readUsername(session: any, service: any): Promise<void> {
        // If the session is already set, the username can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session === undefined) {
            await new Promise((resolve, reject) => {
                setTimeout(resolve, 1000);
            });
        }

        const username = await session.call('localhost.username');
        service.username = username;
    }

    public login(username: string, password: string): boolean {
        // TODO: Send login request to the backend

        // Hard-coded solution
        this.isLoggedIn = true;
        return true;
    }

    public logout(): void {
        this.isLoggedIn = false;
    }
}
