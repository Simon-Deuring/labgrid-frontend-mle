export class Resource {
    public name: string;
    public place: string;
    public target: string;
    public acquired: string;
    public avail: boolean;
    public cls: string;
    public params: {
        address?: string;
        agent_url?: string;
        busnu?: number;
        control_path?: string;
        devnum?: number;
        extra?: object;
        extra_args?: string[];
        gdb_port?: string;
        host?: string;
        hw_server_cmd: string[];
        index?: number;
        log_level?: string[];
        model_id?: number;
        password?: string;
        path?: string;
        pdu?: string;
        port?: number;
        serial?: string;
        speed?: number;
        url?: string;
        username?: string;
        vendor_id?: number;
    };

    // prettier-ignore
    constructor(name: string, place: string, target: string, acquired: string, avail: boolean, cls: string, params: any) {
        this.name = name;
        this.place = place;
        this.target = target;
        this.acquired = acquired;
        this.avail = avail;
        this.cls = cls;
        this.params = params;
    }
}
