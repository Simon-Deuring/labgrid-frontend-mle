import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { LoginService } from './auth/login.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],
})
export class AppComponent {
    title = 'labgrid-web-client';

    constructor(private router: Router, private _ls: LoginService) {}

    navigateToPlaceOverview() {
        this.router.navigate(['/']);
    }

    isLoggedIn(): boolean {
        return this._ls.isLoggedIn;
    }
}
