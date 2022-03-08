import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class LoginService {
    isLoggedIn = true; // Set to false in production mode
    username = '';

    // Store the URL to redirect after logging in
    redirectUrl: string | null = null;

    constructor() {}

    login(username: string, password: string): boolean {
        // TODO: Send login request to the backend

        // Hard-coded solution
        if (username === 'Dummy' && password === 'Passwort123') {
            this.isLoggedIn = true;
            this.username = 'Dummy';

            return true;
        }

        return false;
    }

    logout(): void {
        this.isLoggedIn = false;
    }
}
