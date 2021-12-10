import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Place } from '../../models/place';
import * as autobahn from 'autobahn-browser';

@Injectable({
  providedIn: 'root'
})
export class PlaceService {

  private connection: any;
  private session: any;
  
  constructor(/*private _http: HttpClient*/) {
    const connection = new autobahn.Connection({
      url: 'ws://localhost:8083/ws',
      realm: 'frontend'
    });

    let service = this;
    connection.onopen = async function (session: any, details: any) {
      service.session = session;
    }
    this.connection = connection;

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
      const places = await this.session.call('localhost.places') as Place[];
      const place = places.find(element => element.name === placeName);

      if(!place){
        throw new Error('No such place');
      }
      return place;
    } else {
      await new Promise((resolve, reject) => {
        // The 1000 milliseconds is a critical variable. It may be adapted in the future.
        setTimeout(resolve, 1000);
      });
      const places = await this.session.call('localhost.places') as Place[];
      const place = places.find(element => element.name === placeName);

      if(!place){
        throw new Error('No such place');
      }
      return place;
    }

    // If the python-wamp-client is not available the following line can be used to load test data
    // const place = await this.session.call('localhost.places');
  }

  public getAquiredName(aquired: string): string {
    return aquired.substring(aquired.lastIndexOf('/') + 1)
  }

  public getResourceName(resource: string): string {
    return resource.substring(resource.lastIndexOf('/') + 1)
  }
}
