import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { PlaceService } from '../_services/place.service';
import { ResourceService } from '../_services/resource.service';
import { Resource } from 'src/models/resource';

@Component({
    selector: 'app-resource',
    templateUrl: './resource.component.html',
    styleUrls: ['./resource.component.css'],
})
export class ResourceComponent {
    resource: Resource = new Resource('', '', '', '', false, '', {});
    private placeName: string = '';

    isAcquiredByUser: boolean = false;

    resourceAttributes: Array<{ name: string; value: string }> = [];
    displayedColumns: Array<string> = ['attr-name', 'attr-value'];

    dataReady: boolean = false;

    constructor(
        private _ps: PlaceService,
        private _rs: ResourceService,
        private route: ActivatedRoute,
        private router: Router
    ) {
        route.params.subscribe(() => {
            const resourceName = this.route.snapshot.url[this.route.snapshot.url.length - 1].path;
            // const placeName = this.route.snapshot.paramMap.get('placeName');
            // if (!placeName) {
            //     throw new Error('No place name provided')
            // }
            // this._rs.getResourceByName(resourceName, placeName).then((data) => {
            //     this.resource = data;
            //     this.readResourceAttributes();
            // });

            this._rs.getResourceByName(resourceName, 'placeholdername').then((data) => {
                this.resource = data;
                this.readResourceAttributes();

                if (this.resource.cls === 'NetworkSerialPort') {
                    this.readAcquiringUser();
                }
            });
        });
    }

    private readResourceAttributes(): void {
        if (this.resource.cls) {
            this.resourceAttributes.push({ name: 'Type: ', value: this.resource.cls });
        }
        if (this.resource.place) {
            this.resourceAttributes.push({ name: 'Place name: ', value: this.resource.place });
        }
        if (this.resource.params.host) {
            this.resourceAttributes.push({ name: 'Host name: ', value: this.resource.params.host });
        } else if (this.resource.target) {
            this.resourceAttributes.push({ name: 'Host name: ', value: this.resource.target });
        }
        if (this.resource.params.address) {
            this.resourceAttributes.push({ name: 'Address: ', value: String(this.resource.params.address) });
        }
        if (this.resource.params.port) {
            this.resourceAttributes.push({ name: 'Port: ', value: String(this.resource.params.port) });
        }
        if (this.resource.params.gdb_port) {
            this.resourceAttributes.push({ name: 'GDB port: ', value: String(this.resource.params.gdb_port) });
        }
        if (this.resource.params.username) {
            this.resourceAttributes.push({ name: 'Username: ', value: String(this.resource.params.username) });
        }
        if (this.resource.params.url) {
            this.resourceAttributes.push({ name: 'URL: ', value: String(this.resource.params.url) });
        }
        if (this.resource.params.pdu) {
            this.resourceAttributes.push({ name: 'PDU: ', value: this.resource.params.pdu });
        }
        if (this.resource.params.serial) {
            this.resourceAttributes.push({ name: 'Serial: ', value: this.resource.params.serial });
        }
        if (this.resource.params.index) {
            this.resourceAttributes.push({ name: 'Index:', value: String(this.resource.params.index) });
        }
        if (this.resource.params.speed) {
            this.resourceAttributes.push({ name: 'Speed: ', value: String(this.resource.params.speed) });
        }
        if (this.resource.params.path) {
            this.resourceAttributes.push({ name: 'Path: ', value: this.resource.params.path });
        }
        if (this.resource.params.control_path) {
            this.resourceAttributes.push({ name: 'Control path: ', value: this.resource.params.control_path });
        }
        if (this.resource.acquired) {
            this.resourceAttributes.push({ name: 'Acquired by: ', value: this.resource.acquired });
        }
        if (this.resource.avail != undefined && this.resource.avail != null) {
            this.resourceAttributes.push({ name: 'Available: ', value: String(this.resource.avail) });
        }

        this.dataReady = true;
    }

    private async readAcquiringUser(): Promise<void> {
        const place = await this._ps.getPlace(this.resource.place);

        if (place !== undefined) {
            this.placeName = place.name;

            if (place.acquired === 'labby/dummy') {
                this.isAcquiredByUser = true;
            }
        }
    }

    public startSerialConsole(): void {
        this.router.navigate(['console/', this.placeName]);
    }
}
