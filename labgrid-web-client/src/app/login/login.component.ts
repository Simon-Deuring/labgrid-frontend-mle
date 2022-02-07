import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { LoginService } from '../auth/login.service';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css'],
})
export class LoginComponent implements OnInit {
    ngOnInit(): void {}

    message: string;

    constructor(public ls: LoginService, private router: Router) {
        this.message = this.getMessage();
    }

    getMessage() {
        return 'Logged ' + (this.ls.isLoggedIn ? 'in' : 'out');
    }

    login() {
        this.message = 'Trying to log in ...';

        this.ls.login();
        this.message = this.getMessage();
    }

    logout() {
        this.ls.logout();
        this.message = this.getMessage();
    }
}
