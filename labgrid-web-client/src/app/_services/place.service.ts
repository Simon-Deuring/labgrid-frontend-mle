import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Place } from '../../models/place';
import { AllocationState } from '../_enums/allocation-state';

@Injectable({
  providedIn: 'root'
})
export class PlaceService {

  constructor(private _http: HttpClient) { }

  public async getPlaces(): Promise<Place[]> {
    const places = await this._http.get('../assets/places.json').toPromise() as Place[];

    return places;
  }

  public async getPlace(placeName: string): Promise<Place> {
    const places = await this._http.get('../assets/places.json').toPromise() as Place[];
    const place = places.find(element => element.name === placeName);

    if (!place) {
      throw new Error('No such place');
    }

    return place;
  }

  public getAquiredName(aquired: string): string {
    return aquired.substring(aquired.lastIndexOf('/') + 1)
  }

  public getResourceName(resource: string): string {
    return resource.substring(resource.lastIndexOf('/') + 1)
  }

  public async aquirePlace(placeName: string): Promise<boolean> {
    let body = await this.getPlace(placeName) as Place;

    if ((<any>AllocationState)[body.allocation] === AllocationState.Aquired) {
      console.log('This place is already aquired.');
      return false;
    } else {
      console.log('Place not yet aquired. Try to aquire.');
      // TODO: connect to server 
      return true;
    }
  }

}
