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

  public async getResourceByName(resourceName: string): Promise<Resource> {
    const resources = await this._http.get('../assets/resources.json').toPromise() as Resource[];
    const match = resources.find(element => element.name === resourceName);

    if(!match){
      throw new Error('No such resource');
    }
    
    return match;
  }

  public async getResourcesForPlace(resourceName: string): Promise<Resource[]> {
    const resources = await this._http.get('../assets/resources.json').toPromise() as Resource[];
    const matchingResources = resources.filter(element => element.acquired === resourceName);
    
    return matchingResources;
  }
}
