import { Injectable } from '@angular/core';

import { Place } from '../../models/place';
import { AllocationState } from '../_enums/allocation-state';

import * as autobahn from 'autobahn-browser';

@Injectable({
    providedIn: 'root',
})
export class PlaceService {
    private session: any;

    constructor(/*private _http: HttpClient*/) {
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

    public async getPlaces(): Promise<Place[]> {
        // If the session is already set the places can immediately be read.
        // Otherwise we wait 1 second.
        if (this.session) {
            const places = await this.session.call('localhost.places');
            return places;
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const places = await this.session.call('localhost.places');
            return places;
        }

        // If the python-wamp-client is not available the following line can be used to load test data
        // const places = await this._http.get('../assets/places.json').toPromise() as Place[];
    }

    public async getPlace(placeName: string): Promise<Place> {
        // If the session is already set the places can immediately be read.
        // Otherwise we wait 1 second.
        if (this.session) {
            const places = (await this.session.call('localhost.places')) as Place[];
            const place = places.find((element) => element.name === placeName);

            if (!place) {
                throw new Error('No such place');
            }
            return place;
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const places = (await this.session.call('localhost.places')) as Place[];
            const place = places.find((element) => element.name === placeName);

            if (!place) {
                throw new Error('No such place');
            }
            return place;
        }

        // If the python-wamp-client is not available the following line can be used to load test data
        // const place = await this.session.call('localhost.places');
    }

    public async acquirePlace(placeName: string): Promise<boolean> {
        let body = (await this.getPlace(placeName)) as Place;

        if ((<any>AllocationState)[body.reservation] === AllocationState.Acquired) {
            console.log('This place is already acquired.');
            return false;
        } else {
            console.log('Place not yet acquired. Try to acquire.');
            // TODO: Connect to server
            return true;
        }
    }

    public async releasePlace(placeName: string): Promise<boolean> {
        let body = (await this.getPlace(placeName)) as Place;

        if ((<any>AllocationState)[body.reservation] === AllocationState.Acquired) {
            console.log('Something went wrong while releasing the place.');
            return false;
        } else {
            console.log('Place released successfully.');
            // TODO: Connect to server
            return true;
        }
    }

    public async reservePlace(placeName: string): Promise<boolean> {
        let body = (await this.getPlace(placeName)) as Place;

        if ((<any>AllocationState)[body.reservation] === AllocationState.Acquired) {
            console.log('Something went wrong while reserve the place.');
            return false;
        } else {
            console.log('Place is reserved.');
            // TODO: Connect to server
            return true;
        }
    }
}
