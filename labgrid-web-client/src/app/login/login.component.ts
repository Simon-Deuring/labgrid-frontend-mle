import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { LoginService } from '../auth/login.service';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css'],
})
export class LoginComponent {
    // Used to hide or display the password input
    hide: boolean = true;

    username: string = '';

    password: string = '';

    // If the user enters wrong credentials a warning is displayed
    wrongCredentials: boolean = false;

    // Counts how often the user has inserted a wrong password
    wrongTries: number = 0;

    constructor(public ls: LoginService, private router: Router) {}

    login() {
        if (this.wrongTries < 3 && this.ls.login(this.username, this.password)) {
            // Redirect the user
            const redirectUrl = this.ls.redirectUrl;
            if (redirectUrl == null) {
                this.router.navigate(['/']);
            } else {
                this.router.navigate([redirectUrl]);
            }
        } else {
            this.wrongTries++;
            this.wrongCredentials = true;
        }
    }

    logout() {
        this.ls.logout();
    }
}
