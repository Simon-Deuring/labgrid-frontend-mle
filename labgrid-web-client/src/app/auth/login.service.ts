import { Injectable } from '@angular/core';

@Injectable({
    providedIn: 'root',
})
export class LoginService {
    isLoggedIn = false;
    username = '';

    constructor() {}

    // Store the URL to redirect after logging in
    redirectUrl: string | null = null;

    login(): boolean {
        // TODO: Send login request to the backend
        this.isLoggedIn = true;
        this.username = 'Dummy';

        return true;
    }

    logout(): void {
        this.isLoggedIn = false;
    }
}
