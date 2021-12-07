import { Resource } from "./resource";
import { AllocationState } from "../app/_enums/allocation-state";

export class Place {
    public name: string;
    public matches: string;
    public isRunning: boolean;
    public aquired: string;
    public allocation: string;
    public aquiredResources: string[];

    constructor(name: string, isRunning: boolean, matches: string, aquired: string, allocation: string, aquiredResources: string[]){
        this.name = name;
        this.matches = matches;
        this.isRunning = isRunning;
        this.aquired = aquired;
        this.allocation = allocation;
        this.aquiredResources = aquiredResources;
    }
}