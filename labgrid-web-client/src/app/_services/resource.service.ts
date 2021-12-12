import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Resource } from '../../models/resource';

import * as autobahn from 'autobahn-browser';

@Injectable({
  providedIn: 'root'
})
export class ResourceService {

  private session: any;

  constructor(private _http: HttpClient) {
    const connection = new autobahn.Connection({
      url: 'ws://localhost:8083/ws',
      realm: 'frontend'
    });

    let service = this;
    connection.onopen = async function (session: any, details: any) {
      service.session = session;
    }

    connection.open();
  }

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
