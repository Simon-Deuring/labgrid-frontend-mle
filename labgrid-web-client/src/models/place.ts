export class Place {
    public name: string;
    public matches: string;
    public aquired: string;
    public aquiredResources: string;

    constructor(name: string, matches: string, aquired: string, aquiredResources: string){
        this.name = name;
        this.matches = matches;
        this.aquired = aquired;
        this.aquiredResources = aquiredResources;
    }
}