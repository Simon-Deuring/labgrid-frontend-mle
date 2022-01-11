import { Resource } from './resource';
import { AllocationState } from '../app/_enums/allocation-state';

export class Place {
    public acquired: string;
    public acquired_resources: object[];
    public exporter: string;
    public power_state: boolean;
    public matches: object[];
    public name: string;
    public reservation: AllocationState;

    // prettier-ignore
    constructor(acquired: string, acquired_resources: object[], exporter: string, power_state: boolean, matches: object[], name: string, reservation: AllocationState) {
        this.acquired = acquired;
        this.acquired_resources = acquired_resources;
        this.exporter = exporter;
        this.power_state = power_state;
        this.matches = matches;
        this.name = name;
        this.reservation = reservation;
    }
}
