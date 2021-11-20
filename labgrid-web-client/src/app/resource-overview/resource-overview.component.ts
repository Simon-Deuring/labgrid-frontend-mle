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
  evaluationBoards: Resource[] = [];
  PDUs: Resource[]= [];

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
      if (resource.cls === 'RawSerialPort' || resource.cls === 'NetworkSerialPort' || resource.cls === 'USBSerialPort') {
        this.evaluationBoards.push(resource);
      } else if (resource.cls === 'PDUDaemonPort' || resource.cls.endsWith('PowerPort')) {
        this.PDUs.push(resource);
      }
    })
  }

  public navigateToResource(resourceName: string) {
    this.router.navigate(['resource/', resourceName]);
  }

}
