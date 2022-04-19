import { Injectable } from '@angular/core';

import * as autobahn from 'autobahn-browser';

import { Place } from 'src/models/place';
import { Resource } from 'src/models/resource';

@Injectable({
    providedIn: 'root',
})
export class ResourceService {
    private session: any;

    constructor() {
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

    public async getResources(): Promise<Resource[]> {
        // If the session is already set the places can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session) {
            const resources = (await this.session.call('localhost.resource_overview')) as Resource[];
            return resources;
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const resources = (await this.session.call('localhost.resource_overview')) as Resource[];
            return resources;
        }
    }

    public async getResourcesForPlace(placeName: string): Promise<Resource[]> {
        // If the session is already set the places can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session) {
            const resources = (await this.session.call('localhost.resource_overview', [placeName])) as Resource[];
            return resources;
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const resources = (await this.session.call('localhost.resource_overview', [placeName])) as Resource[];
            return resources;
        }
    }

    public async getResourceByName(resourceName: string, placeName: string): Promise<Resource> {
        // If the session is already set the places can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session) {
            const result = (await this.session.call('localhost.resource_by_name', [resourceName])) as Resource[];
            if (!result) {
                throw new Error('No such resource');
            }
            return result[0];
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const result = (await this.session.call('localhost.resource_by_name', [resourceName])) as Resource[];
            if (!result) {
                throw new Error('No such resource');
            }
            return result[0];
        }
    }

    public async deleteResource(resourceName: string, placeName: string): Promise<Resource> {
        // If the session is already set the data can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session) {
            const result = (await this.session.call('localhost.delete_resource', [
                placeName,
                resourceName,
            ])) as Resource[];
            if (!result) {
                throw new Error('No such resource');
            }
            return result[0];
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const result = (await this.session.call('localhost.delete_resource', [
                placeName,
                resourceName,
            ])) as Resource[];
            if (!result) {
                throw new Error('No such resource');
            }
            return result[0];
        }
    }

    public async createResource(resourceName: string, placeName: string): Promise<Resource> {
        // If the session is already set the data can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session) {
            const result = (await this.session.call('localhost.create_resource', [
                placeName,
                resourceName,
            ])) as Resource[];
            if (!result) {
                throw new Error('No such resource');
            }
            return result[0];
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const result = (await this.session.call('localhost.create_resource', [
                placeName,
                resourceName,
            ])) as Resource[];
            if (!result) {
                throw new Error('No such resource');
            }
            return result[0];
        }
    }

    public async acquireResource(
        resourceName: string,
        place: Place
    ): Promise<{ successful: boolean; errorMessage: string }> {
        // If the session is already set the data can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session) {
            const result = await this.session.call('localhost.acquire_resource', [
                place.name,
                'cup',
                place.name,
                resourceName,
            ]);
            if (!result) {
                throw new Error('No such resource');
            }
            if (result === true) {
                return { successful: true, errorMessage: '' };
            } else {
                return { successful: false, errorMessage: result.error.message };
            }
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const result = await this.session.call('localhost.acquire_resource', [
                place.name,
                'cup',
                place.name,
                resourceName,
            ]);
            if (!result) {
                throw new Error('No such resource');
            }
            if (result === true) {
                return { successful: true, errorMessage: '' };
            } else {
                return { successful: false, errorMessage: result.error.message };
            }
        }
    }

    public async releaseResource(
        resourceName: string,
        place: Place
    ): Promise<{ successful: boolean; errorMessage: string }> {
        // If the session is already set the data can immediately be read.
        // Otherwise the service waits for 1 second.
        if (this.session) {
            const result = await this.session.call('localhost.release_resource', [
                place.name,
                'cup',
                place.name,
                resourceName,
            ]);
            if (!result) {
                throw new Error('Failed to release resource');
            }
            if (result === true) {
                return { successful: true, errorMessage: '' };
            } else {
                return { successful: false, errorMessage: result.error.message };
            }
        } else {
            await new Promise((resolve, reject) => {
                // The 1000 milliseconds is a critical variable. It may be adapted in the future.
                setTimeout(resolve, 1000);
            });
            const result = await this.session.call('localhost.release_resource', [
                place.name,
                'cup',
                place.name,
                resourceName,
            ]);
            if (!result) {
                throw new Error('Failed to release resource');
            }
            if (result === true) {
                return { successful: true, errorMessage: '' };
            } else {
                return { successful: false, errorMessage: result.error.message };
            }
        }
    }
}
