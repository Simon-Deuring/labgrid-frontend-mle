import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Resource } from 'src/models/resource';
import { ResourceService } from '../_services/resource.service';

@Component({
  selector: 'app-resource-overview',
  templateUrl: './resource-overview.component.html',
  styleUrls: ['./resource-overview.component.css']
})
export class ResourceOverviewComponent implements OnInit {

  resources: Resource[] = [];
  serialPorts: Resource[] = [];
  PDUs: Resource[] = [];
  videoStreams: Resource[] = [];
  networkInterfaces: Resource[] = [];
  JTAGResources: Resource[] = [];
  otherResources: Resource[] = [];

  constructor(private _rs: ResourceService, private router: Router) {
    this._rs.getResources().then(data => {
      this.resources = data;
      this.splitResources();
    });
  }

  ngOnInit(): void {

  }

  public splitResources() {
    this.resources.forEach(resource => {
      if (resource.cls.endsWith('SerialPort')) {
        this.serialPorts.push(resource);
      } else if (resource.cls === 'PDUDaemonPort' || resource.cls.endsWith('PowerPort')) {
        this.PDUs.push(resource);
      } else if (resource.cls === 'USBVideo' || resource.cls === 'NetworkUSBVideo' || resource.cls === 'HTTPVideoStream') {
        this.videoStreams.push(resource);
      } else if (resource.cls === 'NetworkService' || resource.cls.endsWith('NetworkInterface')) {
        this.networkInterfaces.push(resource);
      } else if (resource.cls.includes('JTAG') || resource.cls.endsWith('USBDebugger')) {
        this.JTAGResources.push(resource);
      } else {
        this.otherResources.push(resource);
      }
    });
  }

  public navigateToResource(resourceName: string) {
    this.router.navigate(['resource/', resourceName]);
  }

}
