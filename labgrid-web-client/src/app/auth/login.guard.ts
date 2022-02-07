import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';

import { LoginService } from './login.service';

@Injectable({
    providedIn: 'root',
})
export class LoginGuard implements CanActivate {
    constructor(private loginService: LoginService, private router: Router) {}

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): true | UrlTree {
        const url: string = state.url;
        return this.checkLogin(url);
    }

    checkLogin(url: string): true | UrlTree {
        if (this.loginService.isLoggedIn) {
            return true;
        }

        // Store the attempted URL for redirecting
        this.loginService.redirectUrl = url;

        // Cancel the current navigation and redirect to the login page
        return this.router.parseUrl('/login');
    }
}
