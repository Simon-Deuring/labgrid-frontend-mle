import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ResourceService } from '../_services/resource.service';
import { Resource } from 'src/models/resource';

@Component({
  selector: 'app-resource',
  templateUrl: './resource.component.html',
  styleUrls: ['./resource.component.css']
})
export class ResourceComponent implements OnInit {

  resource: Resource = new Resource('', '', '', false, '', {});

  resourceAttributes: Array<{name: string, value: string}> = [];
  displayedColumns: Array<string> = ['attr-name', 'attr-value'];

  dataReady: boolean = false;

  constructor(private _rs: ResourceService, private route: ActivatedRoute) {
    route.params.subscribe(() => {
      const resourceName = route.snapshot.url[route.snapshot.url.length-1].path;
      this._rs.getResourceByName(resourceName).then(data => {
        this.resource = data;
        this.readResourceAttributes();
      });
    })
  }

  ngOnInit(): void {

  }

  private readResourceAttributes(): void {
    if (this.resource.cls) {
      this.resourceAttributes.push({name: 'Type: ', value: this.resource.cls});
    }
    if (this.resource.acquired) {
      this.resourceAttributes.push({name: 'Place name: ', value: this.resource.acquired});
    }
    if (this.resource.avail != undefined && this.resource.avail != null) {
      this.resourceAttributes.push({name: 'Available: ', value: String(this.resource.avail)});
    }
    if (this.resource.params.host) {
      this.resourceAttributes.push({name: 'Host: ', value: this.resource.params.host});
    }
    if (this.resource.params.pdu) {
      this.resourceAttributes.push({name: 'PDU: ', value: this.resource.params.pdu});
    }
    if (this.resource.params.serial) {
      this.resourceAttributes.push({name: 'Serial: ', value: this.resource.params.serial});
    }
    if (this.resource.params.index) {
      this.resourceAttributes.push({name: 'Index:', value: String(this.resource.params.index)});
    }
    if (this.resource.params.port) {
      this.resourceAttributes.push({name: 'Port: ', value: String(this.resource.params.speed)});
    }
    if (this.resource.params.speed) {
      this.resourceAttributes.push({name: 'Speed: ', value: String(this.resource.params.speed)});
    }

    this.dataReady = true;
  }

}
