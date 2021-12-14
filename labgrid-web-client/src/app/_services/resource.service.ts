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
    // If the session is already set the places can immediately be read.
    // Otherwise we wait 1 second.
    if (this.session) {
      const resources = await this.session.call('localhost.resource_by_name');
      return resources;
    } else {
      await new Promise((resolve, reject) => {
        // The 1000 milliseconds is a critical variable. It may be adapted in the future.
        setTimeout(resolve, 1000);
      });
      const resources = await this.session.call('localhost.resource_by_name');
      return resources;
    }

    // If the python-wamp-client is not available the following line can be used to load test data
    // const resources = await this._http.get('../assets/resources.json').toPromise() as Resource[];
  }

  public async getResourceByName(resourceName: string): Promise<Resource> {
    // If the session is already set the places can immediately be read.
    // Otherwise we wait 1 second.
    if (this.session) {
      const result = await this.session.call('localhost.resource_by_name', [resourceName]) as Resource[];
      if (!result) {
        throw new Error('No such resource');
      }
      return result[0];
    } else {
      await new Promise((resolve, reject) => {
        // The 1000 milliseconds is a critical variable. It may be adapted in the future.
        setTimeout(resolve, 1000);
      });
      const result = await this.session.call('localhost.resource_by_name', [resourceName]) as Resource[];
      if (!result) {
        throw new Error('No such resource');
      }
      return result[0];
    }

    // If the python-wamp-client is not available the following line can be used to load test data
    //const resources = await this._http.get('../assets/resources.json').toPromise() as Resource[];
    //const match = resources.find(element => element.name === resourceName);
  }

  public async getResourcesForPlace(resourceName: string): Promise<Resource[]> {
    const resources = await this._http.get('../assets/resources.json').toPromise() as Resource[];
    const matchingResources = resources.filter(element => element.acquired === resourceName);
    
    return matchingResources;
  }
}
