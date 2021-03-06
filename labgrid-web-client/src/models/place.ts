export class Place {
    public acquired: string;
    public acquired_resources: Array<string[]>;
    public exporter: string;
    public power_state: boolean;
    public matches: object[];
    public name: string;
    public reservation: string | null;

    // prettier-ignore
    constructor(acquired: string, acquired_resources: Array<string[]>, exporter: string, power_state: boolean, matches: object[], name: string, reservation: string | null) {
        this.acquired = acquired;
        this.acquired_resources = acquired_resources;
        this.exporter = exporter;
        this.power_state = power_state;
        this.matches = matches;
        this.name = name;
        this.reservation = reservation;
    }
}
