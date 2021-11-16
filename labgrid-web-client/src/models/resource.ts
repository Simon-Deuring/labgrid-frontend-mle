export class Resource {
    public name: string;
    public matches: string;
    public aquired: string;
    public avail: boolean;
    public cls: string;
    public params: object;

    constructor(name: string, matches: string, aquired: string, avail: boolean, cls: string, params: object){
        this.name = name;
        this.matches = matches;
        this.aquired = aquired;
        this.avail = avail;
        this.cls = cls;
        this.params = params;
    }
}