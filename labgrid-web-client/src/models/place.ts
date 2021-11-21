import { Resource } from "./resource";

export class Place {
    public name: string;
    public matches: string;
    public isRunning: boolean;
    public aquired: string;
    public aquiredResources: string[];

    constructor(name: string, isRunning: boolean, matches: string, aquired: string, aquiredResources: string[]){
        this.name = name;
        this.matches = matches;
        this.isRunning = isRunning;
        this.aquired = aquired;
        this.aquiredResources = aquiredResources;
    }
}