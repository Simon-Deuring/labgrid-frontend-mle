import { Resource } from "./resource";
import { AllocationState } from "../app/_enums/allocation-state";

export class Place {
    public acquired: string;
    public acquired_resources: object[];
    public isRunning: boolean;
    public matches: object[];
    public name: string;
    public reservation: AllocationState;
    

    constructor(acquired: string, acquired_resources: object[], isRunning: boolean, matches: object[], name: string, reservation: AllocationState){
        this.acquired = acquired;
        this.acquired_resources = acquired_resources;
        this.isRunning = isRunning;
        this.matches = matches;
        this.name = name;
        this.reservation = reservation;
    }
}