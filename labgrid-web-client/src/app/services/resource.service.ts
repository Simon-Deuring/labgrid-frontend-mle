import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Resource } from '../../models/resource';

@Injectable({
  providedIn: 'root'
})
export class ResourceService {

  constructor(private _http: HttpClient) { }

  public async getResources(): Promise<Resource[]> {
    const resources = await this._http.get('../assets/resources.json').toPromise() as Resource[];
    
    return resources;
  }

  public async getResource(matches: string): Promise<Resource> {
    const resources = await this._http.get('../assets/resources.json').toPromise() as Resource[];
    const resource = resources.find(element => element.matches === matches);

    if(!resource){
      throw new Error('No such resource');
    }
    
    return resource;
  }
}
