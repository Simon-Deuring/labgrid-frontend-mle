export class Resource {
    public name: string;
    public matches: string;
    public acquired: string;
    public avail: boolean;
    public cls: string;
    public params: object;

    constructor(name: string, matches: string, acquired: string, avail: boolean, cls: string, params: object){
        this.name = name;
        this.matches = matches;
        this.acquired = acquired;
        this.avail = avail;
        this.cls = cls;
        this.params = params;
    }
}