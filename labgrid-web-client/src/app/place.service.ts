import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class PlaceService {

  constructor(private _http: HttpClient) { }

  public async getPlaces(): Promise<any> {
    let places: any = [];
    places = await this._http.get('../assets/places.json').toPromise();
    
    return places;
  }
}
